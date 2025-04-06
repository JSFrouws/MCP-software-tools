@echo off
cd %~dp0
dotnet restore XcpParameterVisualizer\XcpParameterVisualizer.csproj
dotnet build XcpParameterVisualizer\XcpParameterVisualizer.csproj
echo Build completed!
