using System;

namespace XcpParameterVisualizer.Models
{
    public class Signal
    {
        public int SignalId { get; set; }
        public int ECUId { get; set; }
        public int? GroupId { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Address { get; set; }
        public string DataType { get; set; } = string.Empty;
        public double? MinValue { get; set; }
        public double? MaxValue { get; set; }
        public string? Units { get; set; }
        public string? Conversion { get; set; }
        public bool IsCalibration { get; set; }
        public bool IsMeasurement { get; set; }
        
        // Runtime properties for visualization
        public double CurrentValue { get; set; }
        public bool IsSelected { get; set; }
        public OxyPlot.OxyColor PlotColor { get; set; } = OxyPlot.OxyColors.Blue;
        
        // For full display in UI
        public string DisplayName => $"{Name} ({Units ?? "no units"})";
        
        // Apply conversion formula to raw value
        public double ConvertValue(double rawValue)
        {
            if (string.IsNullOrEmpty(Conversion))
                return rawValue;
                
            // Simple conversion formula X*factor or X+offset
            if (Conversion.Contains("*"))
            {
                double factor = double.Parse(Conversion.Split('*')[1]);
                return rawValue * factor;
            }
            else if (Conversion.Contains("+"))
            {
                double offset = double.Parse(Conversion.Split('+')[1]);
                return rawValue + offset;
            }
            
            return rawValue;
        }
    }
}
