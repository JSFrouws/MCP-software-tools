using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using XcpParameterVisualizer.A2L;
using XcpParameterVisualizer.Models;
using XcpParameterVisualizer.DataAccess;
using XcpParameterVisualizer.XCP;

namespace XcpParameterVisualizer.Services
{
    public class ParameterAcquisitionService : IDisposable
    {
        private readonly DatabaseService _databaseService;
        private XcpClient? _xcpClient;
        private ECU? _currentEcu;
        private readonly Dictionary<int, Signal> _signalCache = new();
        private readonly Dictionary<string, A2LFile> _a2lCache = new();
        private CancellationTokenSource? _pollingCts;
        
        public event EventHandler<SignalReadingEventArgs>? SignalValueUpdated;
        
        public ParameterAcquisitionService(DatabaseService databaseService)
        {
            _databaseService = databaseService;
        }
        
        public async Task ConnectToEcuAsync(int ecuId)
        {
            // Disconnect any existing connection
            await DisconnectAsync();
            
            // Get ECU details
            _currentEcu = await _databaseService.GetECUByIdAsync(ecuId);
            
            if (_currentEcu == null)
                throw new ArgumentException($"No ECU found with ID {ecuId}");
                
            if (string.IsNullOrEmpty(_currentEcu.IPAddress) || !_currentEcu.Port.HasValue)
                throw new InvalidOperationException($"ECU {_currentEcu.Name} does not have IP address or port defined");
                
            // Create and connect XCP client
            _xcpClient = new XcpClient(_currentEcu.IPAddress, _currentEcu.Port.Value);
            var connected = await _xcpClient.ConnectAsync();
            
            if (!connected)
                throw new Exception($"Failed to connect to ECU {_currentEcu.Name} at {_currentEcu.IPAddress}:{_currentEcu.Port}");
                
            // Parse A2L file if needed
            if (!_a2lCache.ContainsKey(_currentEcu.A2LFilePath))
            {
                var parser = new A2LParser(_currentEcu.A2LFilePath);
                var a2lFile = await parser.ParseAsync();
                _a2lCache[_currentEcu.A2LFilePath] = a2lFile;
            }
        }
        
        public async Task DisconnectAsync()
        {
            // Stop polling if active
            StopPolling();
            
            // Disconnect XCP client
            if (_xcpClient != null)
            {
                await _xcpClient.DisconnectAsync();
                _xcpClient.Dispose();
                _xcpClient = null;
            }
            
            _currentEcu = null;
        }
        
        public async Task<List<Signal>> GetAvailableSignalsAsync(int ecuId)
        {
            // Get signals from the database
            var dbSignals = await _databaseService.GetAllSignalsAsync();
            var ecuSignals = dbSignals.Where(s => s.ECUId == ecuId).ToList();
            
            // Cache signals
            foreach (var signal in ecuSignals)
            {
                _signalCache[signal.SignalId] = signal;
            }
            
            return ecuSignals;
        }
        
        public async Task<double> ReadSignalValueAsync(int signalId)
        {
            if (_xcpClient == null || _currentEcu == null)
                throw new InvalidOperationException("Not connected to an ECU");
                
            // Get the signal
            Signal? signal;
            if (_signalCache.ContainsKey(signalId))
            {
                signal = _signalCache[signalId];
            }
            else
            {
                signal = await _databaseService.GetSignalByIdAsync(signalId);
                if (signal != null)
                {
                    _signalCache[signalId] = signal;
                }
            }
            
            if (signal == null)
                throw new ArgumentException($"No signal found with ID {signalId}");
                
            // Read the value using XCP
            var value = await _xcpClient.ReadParameterAsync(signal);
            
            // Raise event
            OnSignalValueUpdated(new SignalReadingEventArgs(signal, value));
            
            return value;
        }
        
        public void StartPolling(List<int> signalIds, int pollingIntervalMs = 100)
        {
            // Stop any existing polling
            StopPolling();
            
            // Create new cancellation token source
            _pollingCts = new CancellationTokenSource();
            var token = _pollingCts.Token;
            
            // Start polling task
            Task.Run(async () => 
            {
                try
                {
                    while (!token.IsCancellationRequested)
                    {
                        foreach (var signalId in signalIds)
                        {
                            if (token.IsCancellationRequested)
                                break;
                                
                            try
                            {
                                await ReadSignalValueAsync(signalId);
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error reading signal {signalId}: {ex.Message}");
                            }
                        }
                        
                        await Task.Delay(pollingIntervalMs, token);
                    }
                }
                catch (OperationCanceledException)
                {
                    // Normal cancellation
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Polling error: {ex.Message}");
                }
            }, token);
        }
        
        public void StopPolling()
        {
            _pollingCts?.Cancel();
            _pollingCts?.Dispose();
            _pollingCts = null;
        }
        
        protected virtual void OnSignalValueUpdated(SignalReadingEventArgs e)
        {
            SignalValueUpdated?.Invoke(this, e);
        }
        
        public void Dispose()
        {
            StopPolling();
            _xcpClient?.Dispose();
            GC.SuppressFinalize(this);
        }
    }
    
    public class SignalReadingEventArgs : EventArgs
    {
        public Signal Signal { get; }
        public double Value { get; }
        public DateTime Timestamp { get; }
        
        public SignalReadingEventArgs(Signal signal, double value)
        {
            Signal = signal;
            Value = value;
            Timestamp = DateTime.Now;
        }
    }
}
