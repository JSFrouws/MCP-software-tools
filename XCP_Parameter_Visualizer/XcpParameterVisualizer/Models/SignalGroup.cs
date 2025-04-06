using System.Collections.Generic;

namespace XcpParameterVisualizer.Models
{
    public class SignalGroup
    {
        public int GroupId { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public int ECUId { get; set; }
        
        public List<Signal> Signals { get; set; } = new List<Signal>();
    }
}
