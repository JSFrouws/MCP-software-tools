using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using OxyPlot;
using OxyPlot.Axes;
using OxyPlot.Series;
using OxyPlot.Legends;
using XcpParameterVisualizer.DataAccess;
using XcpParameterVisualizer.Models;
using XcpParameterVisualizer.Services;

namespace XcpParameterVisualizer.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private readonly DatabaseService _databaseService;
        private readonly ParameterAcquisitionService _acquisitionService;
        private readonly DispatcherTimer _uiUpdateTimer;
        private readonly Dictionary<int, List<OxyPlot.DataPoint>> _signalDataPoints = new();
        private readonly Dictionary<int, int> _signalPointCount = new();
        private readonly Random _random = new();
        private const int MaxPointsPerSignal = 1000;

        private ObservableCollection<ECU> _ecus = new();
        private ObservableCollection<Signal> _availableSignals = new();
        private ObservableCollection<Signal> _selectedSignals = new();
        private ECU? _selectedEcu;
        private Signal? _selectedAvailableSignal;
        private Signal? _selectedMonitoredSignal;
        private string _connectionStatus = "Disconnected";
        private bool _isConnected;
        private PlotModel _plotModel = new();
        private string _statusMessage = string.Empty;
        private bool _isLoading;

        public ObservableCollection<ECU> ECUs
        {
            get => _ecus;
            set => SetProperty(ref _ecus, value);
        }

        public ObservableCollection<Signal> AvailableSignals
        {
            get => _availableSignals;
            set => SetProperty(ref _availableSignals, value);
        }

        public ObservableCollection<Signal> SelectedSignals
        {
            get => _selectedSignals;
            set => SetProperty(ref _selectedSignals, value);
        }

        public ECU? SelectedEcu
        {
            get => _selectedEcu;
            set
            {
                if (SetProperty(ref _selectedEcu, value) && value != null)
                {
                    LoadSignalsForEcu(value.ECUId);
                }
            }
        }

        public Signal? SelectedAvailableSignal
        {
            get => _selectedAvailableSignal;
            set => SetProperty(ref _selectedAvailableSignal, value);
        }

        public Signal? SelectedMonitoredSignal
        {
            get => _selectedMonitoredSignal;
            set => SetProperty(ref _selectedMonitoredSignal, value);
        }

        public string ConnectionStatus
        {
            get => _connectionStatus;
            set => SetProperty(ref _connectionStatus, value);
        }

        public bool IsConnected
        {
            get => _isConnected;
            set
            {
                if (SetProperty(ref _isConnected, value))
                {
                    ((RelayCommand)ConnectCommand).RaiseCanExecuteChanged();
                    ((RelayCommand)DisconnectCommand).RaiseCanExecuteChanged();
                }
            }
        }

        public PlotModel PlotModel
        {
            get => _plotModel;
            set => SetProperty(ref _plotModel, value);
        }

        public string StatusMessage
        {
            get => _statusMessage;
            set => SetProperty(ref _statusMessage, value);
        }

        public bool IsLoading
        {
            get => _isLoading;
            set => SetProperty(ref _isLoading, value);
        }

        public ICommand ConnectCommand { get; }
        public ICommand DisconnectCommand { get; }
        public ICommand AddSignalCommand { get; }
        public ICommand RemoveSignalCommand { get; }
        public ICommand ClearPlotCommand { get; }

        public MainViewModel(string connectionString)
        {
            _databaseService = new DatabaseService(connectionString);
            _acquisitionService = new ParameterAcquisitionService(_databaseService);
            _acquisitionService.SignalValueUpdated += OnSignalValueUpdated;

            // Initialize commands
            ConnectCommand = new RelayCommand(_ => ConnectToEcu(), _ => SelectedEcu != null && !IsConnected);
            DisconnectCommand = new RelayCommand(_ => Disconnect(), _ => IsConnected);
            AddSignalCommand = new RelayCommand(_ => AddSignalToMonitoring(), _ => SelectedAvailableSignal != null && IsConnected);
            RemoveSignalCommand = new RelayCommand(_ => RemoveSignalFromMonitoring(), _ => SelectedMonitoredSignal != null);
            ClearPlotCommand = new RelayCommand(_ => ClearPlot());

            // Initialize plot model
            InitializePlotModel();

            // Create UI update timer for plot
            _uiUpdateTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(100)
            };
            _uiUpdateTimer.Tick += (_, _) => UpdatePlot();
            _uiUpdateTimer.Start();

            // Load ECUs
            Task.Run(LoadEcusAsync);
        }

        private void InitializePlotModel()
        {
            PlotModel = new PlotModel
            {
                Title = "Parameter Visualization",
                LegendPosition = OxyPlot.LegendPosition.RightBottom,
                LegendPlacement = OxyPlot.LegendPlacement.Outside
            };

            // Add axes
            PlotModel.Axes.Add(new DateTimeAxis
            {
                Position = AxisPosition.Bottom,
                Title = "Time",
                StringFormat = "HH:mm:ss",
                MajorGridlineStyle = LineStyle.Dot,
                MinorGridlineStyle = LineStyle.Dot
            });

            PlotModel.Axes.Add(new LinearAxis
            {
                Position = AxisPosition.Left,
                Title = "Value",
                MajorGridlineStyle = LineStyle.Dot,
                MinorGridlineStyle = LineStyle.Dot
            });
        }

        private async Task LoadEcusAsync()
        {
            IsLoading = true;
            StatusMessage = "Loading ECUs...";

            try
            {
                var ecus = await _databaseService.GetAllECUsAsync();
                
                Application.Current.Dispatcher.Invoke(() =>
                {
                    ECUs.Clear();
                    foreach (var ecu in ecus)
                    {
                        ECUs.Add(ecu);
                    }
                    
                    if (ecus.Count > 0)
                    {
                        SelectedEcu = ecus[0];
                    }
                    
                    StatusMessage = $"Loaded {ecus.Count} ECUs";
                });
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error loading ECUs: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async void LoadSignalsForEcu(int ecuId)
        {
            IsLoading = true;
            StatusMessage = "Loading signals...";

            try
            {
                var signals = await _acquisitionService.GetAvailableSignalsAsync(ecuId);
                
                Application.Current.Dispatcher.Invoke(() =>
                {
                    AvailableSignals.Clear();
                    foreach (var signal in signals)
                    {
                        AvailableSignals.Add(signal);
                    }
                    
                    StatusMessage = $"Loaded {signals.Count} signals for ECU {SelectedEcu?.Name}";
                });
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error loading signals: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async void ConnectToEcu()
        {
            if (SelectedEcu == null) return;

            IsLoading = true;
            StatusMessage = $"Connecting to ECU {SelectedEcu.Name}...";

            try
            {
                await _acquisitionService.ConnectToEcuAsync(SelectedEcu.ECUId);
                IsConnected = true;
                ConnectionStatus = $"Connected to {SelectedEcu.Name}";
                StatusMessage = $"Successfully connected to ECU {SelectedEcu.Name}";
            }
            catch (Exception ex)
            {
                IsConnected = false;
                ConnectionStatus = "Disconnected";
                StatusMessage = $"Connection error: {ex.Message}";
                
                // In a real application, we might use simulation mode here
                MessageBox.Show($"Failed to connect to ECU: {ex.Message}\n\nThe application will continue in simulation mode.", 
                    "Connection Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                
                // For demo purposes, we'll still allow signal selection in a "connected" state
                IsConnected = true;
                ConnectionStatus = $"Simulation: {SelectedEcu.Name}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async void Disconnect()
        {
            IsLoading = true;
            StatusMessage = "Disconnecting...";

            try
            {
                await _acquisitionService.DisconnectAsync();
                
                // Clear selected signals
                SelectedSignals.Clear();
                
                // Clear plot data
                ClearPlot();
                
                IsConnected = false;
                ConnectionStatus = "Disconnected";
                StatusMessage = "Disconnected from ECU";
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error disconnecting: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        private void AddSignalToMonitoring()
        {
            if (SelectedAvailableSignal == null) return;
            
            if (!SelectedSignals.Any(s => s.SignalId == SelectedAvailableSignal.SignalId))
            {
                var signal = SelectedAvailableSignal;
                
                // Assign a random color for the signal's plot
                signal.PlotColor = OxyColor.FromArgb(255, 
                    (byte)_random.Next(20, 230), 
                    (byte)_random.Next(20, 230), 
                    (byte)_random.Next(20, 230));
                
                SelectedSignals.Add(signal);
                
                // Add series to plot
                var lineSeries = new LineSeries
                {
                    Title = signal.DisplayName,
                    Color = signal.PlotColor,
                    StrokeThickness = 2,
                    MarkerType = MarkerType.Circle,
                    MarkerSize = 3,
                    MarkerStroke = signal.PlotColor,
                    MarkerFill = signal.PlotColor,
                    Tag = signal.SignalId // Store the SignalId for identification
                };
                
                PlotModel.Series.Add(lineSeries);
                
                // Initialize data points collection for this signal
                _signalDataPoints[signal.SignalId] = new List<DataPoint>();
                _signalPointCount[signal.SignalId] = 0;
                
                // Start polling if this is the first signal added
                if (SelectedSignals.Count == 1)
                {
                    StartPolling();
                }
                
                StatusMessage = $"Added signal {signal.Name} to monitoring";
                PlotModel.InvalidatePlot(true);
            }
        }

        private void RemoveSignalFromMonitoring()
        {
            if (SelectedMonitoredSignal == null) return;
            
            var signalId = SelectedMonitoredSignal.SignalId;
            
            // Remove from selected signals
            SelectedSignals.Remove(SelectedMonitoredSignal);
            
            // Remove series from plot
            var seriesToRemove = PlotModel.Series.FirstOrDefault(s => (int)s.Tag == signalId);
            if (seriesToRemove != null)
            {
                PlotModel.Series.Remove(seriesToRemove);
            }
            
            // Remove data points
            _signalDataPoints.Remove(signalId);
            _signalPointCount.Remove(signalId);
            
            // Stop polling if no more signals
            if (SelectedSignals.Count == 0)
            {
                _acquisitionService.StopPolling();
            }
            else
            {
                // Update polling with remaining signals
                StartPolling();
            }
            
            StatusMessage = $"Removed signal {SelectedMonitoredSignal.Name} from monitoring";
            PlotModel.InvalidatePlot(true);
        }

        private void StartPolling()
        {
            if (SelectedSignals.Count == 0) return;
            
            var signalIds = SelectedSignals.Select(s => s.SignalId).ToList();
            _acquisitionService.StartPolling(signalIds);
        }

        private void OnSignalValueUpdated(object? sender, SignalReadingEventArgs e)
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                // In a real application, this would be a real value from the ECU
                double value = e.Value;
                
                // For simulation purposes, if we're not really connected to an ECU
                if (ConnectionStatus.StartsWith("Simulation"))
                {
                    // Generate simulated data that looks like real sensor values
                    var signal = e.Signal;
                    double min = signal.MinValue ?? 0;
                    double max = signal.MaxValue ?? 100;
                    double range = max - min;
                    
                    // Use a sine wave with some noise for a realistic looking signal
                    var count = _signalPointCount.ContainsKey(signal.SignalId) ? _signalPointCount[signal.SignalId] : 0;
                    
                    // A different frequency for each signal
                    var frequency = (signal.SignalId % 5 + 1) * 0.01;
                    
                    // Base sine wave
                    value = min + range * 0.5 * (1 + Math.Sin(count * frequency));
                    
                    // Add some noise
                    value += _random.NextDouble() * range * 0.05 - range * 0.025;
                    
                    // Keep within bounds
                    value = Math.Max(min, Math.Min(max, value));
                    
                    _signalPointCount[signal.SignalId] = count + 1;
                }
                
                if (_signalDataPoints.TryGetValue(e.Signal.SignalId, out var dataPoints))
                {
                    var time = DateTimeAxis.ToDouble(DateTime.Now);
                    dataPoints.Add(new DataPoint(time, value));
                    
                    // Limit the number of points to avoid memory issues
                    if (dataPoints.Count > MaxPointsPerSignal)
                    {
                        dataPoints.RemoveAt(0);
                    }
                }
            });
        }

        private void UpdatePlot()
        {
            // Find each series and update with current data points
            foreach (var series in PlotModel.Series.OfType<LineSeries>())
            {
                if (series.Tag is int signalId && _signalDataPoints.ContainsKey(signalId))
                {
                    var dataPoints = _signalDataPoints[signalId];
                    series.Points.Clear();
                    series.Points.AddRange(dataPoints);
                }
            }
            
            // Auto-scale axes
            foreach (var axis in PlotModel.Axes)
            {
                axis.Maximum = double.NaN;
                axis.Minimum = double.NaN;
            }
            
            // Update plot
            PlotModel.InvalidatePlot(true);
        }

        private void ClearPlot()
        {
            foreach (var signalId in _signalDataPoints.Keys.ToList())
            {
                _signalDataPoints[signalId].Clear();
                _signalPointCount[signalId] = 0;
            }
            
            PlotModel.InvalidatePlot(true);
            StatusMessage = "Plot cleared";
        }
    }
}
