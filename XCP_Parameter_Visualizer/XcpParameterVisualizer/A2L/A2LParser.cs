using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using XcpParameterVisualizer.Models;

namespace XcpParameterVisualizer.A2L
{
    public class A2LParser
    {
        private readonly string _filePath;
        
        public A2LParser(string filePath)
        {
            if (!File.Exists(filePath))
                throw new FileNotFoundException($"A2L file not found: {filePath}");
                
            _filePath = filePath;
        }
        
        public async Task<A2LFile> ParseAsync()
        {
            var a2lContent = await File.ReadAllTextAsync(_filePath);
            return Parse(a2lContent);
        }
        
        public A2LFile Parse(string content)
        {
            var a2lFile = new A2LFile
            {
                FilePath = _filePath,
                Measurements = new List<Measurement>(),
                Characteristics = new List<Characteristic>()
            };
            
            // Extract project name
            var projectMatch = Regex.Match(content, @"/begin\s+PROJECT\s+(\w+)");
            if (projectMatch.Success)
            {
                a2lFile.ProjectName = projectMatch.Groups[1].Value;
            }
            
            // Extract module name
            var moduleMatch = Regex.Match(content, @"/begin\s+MODULE\s+(\w+)");
            if (moduleMatch.Success)
            {
                a2lFile.ModuleName = moduleMatch.Groups[1].Value;
            }
            
            // Parse measurements (signals)
            var measurementMatches = Regex.Matches(content, 
                @"/begin\s+MEASUREMENT\s+(\w+)[\s\S]*?ADDR_EPK\s+([0-9xA-Fa-f]+)[\s\S]*?DATATYPE\s+(\w+)[\s\S]*?/end\s+MEASUREMENT");
            
            foreach (Match match in measurementMatches)
            {
                var name = match.Groups[1].Value;
                var address = match.Groups[2].Value;
                var dataType = match.Groups[3].Value;
                
                // Extract additional info
                var text = match.Value;
                var description = ExtractValue(text, "LONGIDENTIFIER", "\"([^\"]*)\"");
                var units = ExtractValue(text, "UNIT", "\"([^\"]*)\"");
                
                var measurement = new Measurement
                {
                    Name = name,
                    Address = address,
                    DataType = dataType,
                    Description = description,
                    Units = units
                };
                
                // Extract COMPU_METHOD for conversion formula
                var compuMethodName = ExtractValue(text, "COMPU_METHOD", @"\s+(\w+)");
                if (!string.IsNullOrEmpty(compuMethodName))
                {
                    var compuMethodMatch = Regex.Match(content, $@"/begin\s+COMPU_METHOD\s+{compuMethodName}[\s\S]*?COMPU_RATIONAL_COEFFS[\s\S]*?COEFFS\s+([-0-9.eE\s]+)[\s\S]*?/end\s+COMPU_METHOD");
                    
                    if (compuMethodMatch.Success)
                    {
                        var coeffsStr = compuMethodMatch.Groups[1].Value.Trim();
                        var coeffs = coeffsStr.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                        
                        if (coeffs.Length >= 2)
                        {
                            double a = double.Parse(coeffs[0]);
                            double b = double.Parse(coeffs[1]);
                            
                            if (a != 0)
                                measurement.Conversion = $"X*{b/a}";
                            else if (b != 0)
                                measurement.Conversion = $"X+{b}";
                        }
                    }
                }
                
                a2lFile.Measurements.Add(measurement);
            }
            
            // Parse characteristics (calibration parameters)
            var characteristicMatches = Regex.Matches(content, 
                @"/begin\s+CHARACTERISTIC\s+(\w+)[\s\S]*?ADDR_EPK\s+([0-9xA-Fa-f]+)[\s\S]*?TYPE\s+(\w+)[\s\S]*?/end\s+CHARACTERISTIC");
            
            foreach (Match match in characteristicMatches)
            {
                var name = match.Groups[1].Value;
                var address = match.Groups[2].Value;
                var type = match.Groups[3].Value;
                
                var text = match.Value;
                var description = ExtractValue(text, "LONGIDENTIFIER", "\"([^\"]*)\"");
                
                var characteristic = new Characteristic
                {
                    Name = name,
                    Address = address,
                    Type = type,
                    Description = description
                };
                
                a2lFile.Characteristics.Add(characteristic);
            }
            
            return a2lFile;
        }
        
        private string? ExtractValue(string text, string keyword, string pattern)
        {
            var regex = new Regex($@"{keyword}\s+{pattern}");
            var match = regex.Match(text);
            return match.Success ? match.Groups[1].Value : null;
        }
    }
    
    public class A2LFile
    {
        public string FilePath { get; set; } = string.Empty;
        public string ProjectName { get; set; } = string.Empty;
        public string ModuleName { get; set; } = string.Empty;
        public List<Measurement> Measurements { get; set; } = new List<Measurement>();
        public List<Characteristic> Characteristics { get; set; } = new List<Characteristic>();
    }
    
    public class Measurement
    {
        public string Name { get; set; } = string.Empty;
        public string Address { get; set; } = string.Empty;
        public string DataType { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Units { get; set; }
        public string? Conversion { get; set; }
        public double MinValue { get; set; }
        public double MaxValue { get; set; }
        
        // Convert to a Signal model
        public Signal ToSignal(int ecuId)
        {
            return new Signal
            {
                ECUId = ecuId,
                Name = Name,
                Description = Description,
                Address = Address,
                DataType = DataType,
                Units = Units,
                Conversion = Conversion,
                MinValue = MinValue,
                MaxValue = MaxValue,
                IsCalibration = false,
                IsMeasurement = true
            };
        }
    }
    
    public class Characteristic
    {
        public string Name { get; set; } = string.Empty;
        public string Address { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Units { get; set; }
        public string? Conversion { get; set; }
        
        // Convert to a Signal model (for calibration parameters)
        public Signal ToSignal(int ecuId)
        {
            return new Signal
            {
                ECUId = ecuId,
                Name = Name,
                Description = Description,
                Address = Address,
                DataType = Type,
                Units = Units,
                Conversion = Conversion,
                IsCalibration = true,
                IsMeasurement = false
            };
        }
    }
}
