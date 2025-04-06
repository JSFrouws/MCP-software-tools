using System;
using System.Collections.Generic;

namespace XcpParameterVisualizer.Models
{
    public class ECU
    {
        public int ECUId { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string A2LFilePath { get; set; } = string.Empty;
        public string XCPProtocol { get; set; } = "Ethernet";
        public string? IPAddress { get; set; }
        public int? Port { get; set; }
        public string? CANInterface { get; set; }
        public int? CANId { get; set; }
        
        public List<SignalGroup> SignalGroups { get; set; } = new List<SignalGroup>();
    }
}
