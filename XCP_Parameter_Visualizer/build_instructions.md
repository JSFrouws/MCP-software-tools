# Build Instructions for XCP Parameter Visualizer

This document provides instructions for building the XCP Parameter Visualizer application using the .NET CLI.

## Prerequisites

- .NET SDK 8.0 or higher
- Visual Studio 2022 or Visual Studio Code (optional)
- SQL Server (for database functionality)

## Building from the Command Line

1. **Clone the repository (if you haven't already)**
   ```
   git clone <repository-url>
   cd XCP_Parameter_Visualizer
   ```

2. **Restore NuGet packages**
   ```
   dotnet restore XcpParameterVisualizer/XcpParameterVisualizer.csproj
   ```

3. **Build the project**
   ```
   dotnet build XcpParameterVisualizer/XcpParameterVisualizer.csproj --configuration Release
   ```

4. **Run the application**
   ```
   dotnet run --project XcpParameterVisualizer/XcpParameterVisualizer.csproj
   ```

## Building with Visual Studio

1. Open the `XcpParameterVisualizer.sln` file with Visual Studio
2. Right-click on the solution in Solution Explorer and select "Restore NuGet Packages"
3. Build the solution using the Build menu or by pressing F6
4. Run the application using the Debug menu or by pressing F5

## Database Setup

Before running the application, make sure to set up the SQL database:

1. Open SQL Server Management Studio or another SQL client
2. Connect to your SQL Server instance
3. Run the SQL script located at `Database/SignalDatabase.sql`
4. Update the connection string in `MainWindow.xaml.cs` to match your SQL Server configuration

## Troubleshooting Common Build Issues

### NuGet Package Restore Issues

If you encounter errors during package restore, try:

```
dotnet nuget locals all --clear
```

Then attempt to restore packages again.

### .NET SDK Version Issues

If you encounter framework compatibility issues, ensure you have the correct .NET SDK installed:

```
dotnet --version
```

This project requires .NET 8.0 or later.

### Windows-Specific Features

This application uses WPF, which is only available on Windows. If you're on a non-Windows platform, consider using the .NET MAUI or Avalonia versions (if available).
