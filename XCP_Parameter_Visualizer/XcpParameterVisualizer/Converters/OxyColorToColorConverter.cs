using System;
using System.Windows.Data;
using System.Windows.Media;
using OxyPlot;

namespace XcpParameterVisualizer.Converters
{
    /// <summary>
    /// Converter for OxyPlot's OxyColor to WPF Color
    /// </summary>
    public class OxyColorToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            if (value is OxyColor oxyColor)
            {
                return Color.FromArgb(oxyColor.A, oxyColor.R, oxyColor.G, oxyColor.B);
            }
            
            return Colors.Black;
        }

        public object ConvertBack(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            if (value is Color color)
            {
                return OxyColor.FromArgb(color.A, color.R, color.G, color.B);
            }
            
            return OxyColors.Black;
        }
    }
}
