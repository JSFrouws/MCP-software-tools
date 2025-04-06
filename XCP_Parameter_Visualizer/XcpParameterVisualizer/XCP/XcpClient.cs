using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using XcpParameterVisualizer.Models;

namespace XcpParameterVisualizer.XCP
{
    public class XcpClient : IDisposable
    {
        // XCP Command Codes (based on XCP 1.0 specification)
        private const byte CMD_CONNECT = 0xFF;
        private const byte CMD_DISCONNECT = 0xFE;
        private const byte CMD_GET_STATUS = 0xFD;
        private const byte CMD_SYNCH = 0xFC;
        private const byte CMD_GET_COMM_MODE_INFO = 0xFB;
        private const byte CMD_GET_ID = 0xFA;
        private const byte CMD_SET_REQUEST = 0xF9;
        private const byte CMD_GET_SEED = 0xF8;
        private const byte CMD_UNLOCK = 0xF7;
        private const byte CMD_SET_MTA = 0xF6;
        private const byte CMD_UPLOAD = 0xF5;
        private const byte CMD_SHORT_UPLOAD = 0xF4;
        private const byte CMD_BUILD_CHECKSUM = 0xF3;
        private const byte CMD_TRANSPORT_LAYER_CMD = 0xF2;
        private const byte CMD_USER_CMD = 0xF1;
        
        // XCP Positive Response
        private const byte PID_OK = 0xFF;
        
        // Connection modes
        private const byte CONNECT_MODE_NORMAL = 0x00;
        
        // XCP Protocol layer version
        private const byte PROTOCOL_LAYER_VERSION = 0x01;
        
        private TcpClient? _tcpClient;
        private NetworkStream? _stream;
        private readonly string _hostname;
        private readonly int _port;
        private bool _isConnected;
        private readonly object _sendLock = new();
        
        public XcpClient(string hostname, int port)
        {
            _hostname = hostname;
            _port = port;
            _isConnected = false;
        }
        
        public async Task<bool> ConnectAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                _tcpClient = new TcpClient();
                await _tcpClient.ConnectAsync(_hostname, _port, cancellationToken);
                _stream = _tcpClient.GetStream();
                
                // XCP CONNECT command
                byte[] connectCmd = new byte[2] { CMD_CONNECT, CONNECT_MODE_NORMAL };
                byte[] response = await SendCommandAsync(connectCmd, cancellationToken);
                
                if (response.Length > 0 && response[0] == PID_OK)
                {
                    _isConnected = true;
                    return true;
                }
                
                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"XCP connection error: {ex.Message}");
                return false;
            }
        }
        
        public async Task DisconnectAsync(CancellationToken cancellationToken = default)
        {
            if (_isConnected && _stream != null)
            {
                byte[] disconnectCmd = new byte[1] { CMD_DISCONNECT };
                await SendCommandAsync(disconnectCmd, cancellationToken);
                _isConnected = false;
            }
            
            _stream?.Close();
            _tcpClient?.Close();
        }
        
        public async Task<double> ReadParameterAsync(Signal signal, CancellationToken cancellationToken = default)
        {
            if (!_isConnected || _stream == null)
                throw new InvalidOperationException("XCP client is not connected");
                
            if (string.IsNullOrEmpty(signal.Address))
                throw new ArgumentException("Signal address is missing");
                
            try
            {
                // Parse address (assuming hex format like 0x12345678)
                if (!signal.Address.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("Address must be in hexadecimal format (0x...)");
                    
                var addressStr = signal.Address.Substring(2);
                uint address = Convert.ToUInt32(addressStr, 16);
                
                // Determine size based on the data type
                int size = GetDataTypeSize(signal.DataType);
                
                // Use SHORT_UPLOAD command for optimized memory read
                byte[] cmd = new byte[8];
                cmd[0] = CMD_SHORT_UPLOAD;
                cmd[1] = 0x00; // Reserved field
                cmd[2] = (byte)size; // Size of data to read
                cmd[3] = 0x00; // Address extension (0 for standard memory)
                
                // Address (little-endian)
                cmd[4] = (byte)(address & 0xFF);
                cmd[5] = (byte)((address >> 8) & 0xFF);
                cmd[6] = (byte)((address >> 16) & 0xFF);
                cmd[7] = (byte)((address >> 24) & 0xFF);
                
                byte[] response = await SendCommandAsync(cmd, cancellationToken);
                
                if (response.Length > 0 && response[0] == PID_OK)
                {
                    // Parse the data according to the data type
                    double value = ParseData(response, 1, signal.DataType);
                    
                    // Apply conversion if available
                    if (!string.IsNullOrEmpty(signal.Conversion))
                        value = signal.ConvertValue(value);
                        
                    return value;
                }
                
                throw new Exception("Failed to read parameter: XCP command failed");
            }
            catch (Exception ex)
            {
                throw new Exception($"Error reading parameter {signal.Name}: {ex.Message}", ex);
            }
        }
        
        private async Task<byte[]> SendCommandAsync(byte[] command, CancellationToken cancellationToken = default)
        {
            if (_stream == null)
                throw new InvalidOperationException("XCP client is not connected");
                
            // XCP on Ethernet uses a 16-bit length header followed by the command
            byte[] packet = new byte[command.Length + 2];
            packet[0] = (byte)(command.Length & 0xFF); // Length LSB
            packet[1] = (byte)((command.Length >> 8) & 0xFF); // Length MSB
            Array.Copy(command, 0, packet, 2, command.Length);
            
            lock (_sendLock)
            {
                _stream.Write(packet, 0, packet.Length);
            }
            
            // Read response length (2 bytes)
            byte[] lengthBytes = new byte[2];
            int bytesRead = await _stream.ReadAsync(lengthBytes, 0, 2, cancellationToken);
            
            if (bytesRead != 2)
                throw new Exception("Failed to read XCP response length");
                
            int responseLength = lengthBytes[0] | (lengthBytes[1] << 8);
            
            // Read response data
            byte[] response = new byte[responseLength];
            bytesRead = await _stream.ReadAsync(response, 0, responseLength, cancellationToken);
            
            if (bytesRead != responseLength)
                throw new Exception("Failed to read complete XCP response");
                
            return response;
        }
        
        private int GetDataTypeSize(string dataType)
        {
            return dataType.ToUpperInvariant() switch
            {
                "UBYTE" => 1,
                "BYTE" => 1,
                "UINT8" => 1,
                "INT8" => 1,
                "UWORD" => 2,
                "WORD" => 2,
                "UINT16" => 2,
                "INT16" => 2,
                "ULONG" => 4,
                "LONG" => 4,
                "UINT32" => 4,
                "INT32" => 4,
                "FLOAT32" => 4,
                "FLOAT64" => 8,
                _ => throw new ArgumentException($"Unsupported data type: {dataType}")
            };
        }
        
        private double ParseData(byte[] data, int offset, string dataType)
        {
            switch (dataType.ToUpperInvariant())
            {
                case "UBYTE":
                case "UINT8":
                    return data[offset];
                    
                case "BYTE":
                case "INT8":
                    return (sbyte)data[offset];
                    
                case "UWORD":
                case "UINT16":
                    return BitConverter.ToUInt16(data, offset);
                    
                case "WORD":
                case "INT16":
                    return BitConverter.ToInt16(data, offset);
                    
                case "ULONG":
                case "UINT32":
                    return BitConverter.ToUInt32(data, offset);
                    
                case "LONG":
                case "INT32":
                    return BitConverter.ToInt32(data, offset);
                    
                case "FLOAT32":
                    return BitConverter.ToSingle(data, offset);
                    
                case "FLOAT64":
                    return BitConverter.ToDouble(data, offset);
                    
                default:
                    throw new ArgumentException($"Unsupported data type: {dataType}");
            }
        }
        
        public void Dispose()
        {
            _stream?.Dispose();
            _tcpClient?.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}
