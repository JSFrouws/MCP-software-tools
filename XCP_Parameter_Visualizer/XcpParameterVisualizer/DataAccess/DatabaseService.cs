using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Data.SqlClient;
using Dapper;
using XcpParameterVisualizer.Models;

namespace XcpParameterVisualizer.DataAccess
{
    public class DatabaseService
    {
        private readonly string _connectionString;
        
        public DatabaseService(string connectionString)
        {
            _connectionString = connectionString;
        }
        
        public async Task<List<ECU>> GetAllECUsAsync()
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync();
            
            var ecus = await connection.QueryAsync<ECU>("SELECT * FROM ECUs");
            return ecus.ToList();
        }
        
        public async Task<List<SignalGroup>> GetSignalGroupsByECUIdAsync(int ecuId)
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync();
            
            var groups = await connection.QueryAsync<SignalGroup>(
                "SELECT * FROM SignalGroups WHERE ECUId = @ECUId",
                new { ECUId = ecuId });
                
            return groups.ToList();
        }
        
        public async Task<List<Signal>> GetSignalsByGroupIdAsync(int groupId)
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync();
            
            var signals = await connection.QueryAsync<Signal>(
                "SELECT * FROM Signals WHERE GroupId = @GroupId",
                new { GroupId = groupId });
                
            return signals.ToList();
        }
        
        public async Task<List<Signal>> GetAllSignalsAsync()
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync();
            
            var signals = await connection.QueryAsync<Signal>("SELECT * FROM Signals");
            return signals.ToList();
        }
        
        public async Task<Signal?> GetSignalByIdAsync(int signalId)
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync();
            
            return await connection.QueryFirstOrDefaultAsync<Signal>(
                "SELECT * FROM Signals WHERE SignalId = @SignalId",
                new { SignalId = signalId });
        }
        
        public async Task<ECU?> GetECUByIdAsync(int ecuId)
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync();
            
            return await connection.QueryFirstOrDefaultAsync<ECU>(
                "SELECT * FROM ECUs WHERE ECUId = @ECUId",
                new { ECUId = ecuId });
        }
    }
}
