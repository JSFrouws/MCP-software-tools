using System;

namespace XcpParameterVisualizer.Models
{
    public class SignalReading
    {
        public int SignalId { get; set; }
        public DateTime Timestamp { get; set; }
        public double Value { get; set; }
        
        // Reference to the signal metadata
        public Signal? Signal { get; set; }
    }
}
