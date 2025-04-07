# XCP Parameter Visualizer

A C# application that uses the XCP protocol and A2L files to extract parameters from automotive ECUs and visualize them in real-time graphs.

## Overview

This application provides a user-friendly interface for automotive engineers and calibrators to connect to ECUs via XCP protocol, extract parameters defined in A2L files, and monitor them in real-time through dynamic graphs.

## Features

- Connect to ECUs using the XCP protocol over Ethernet
- Parse A2L files to understand available parameters
- Pull signal metadata from a SQL database
- Select signals from a dropdown menu to monitor
- Visualize multiple signals simultaneously on a time-series graph
- Real-time data acquisition and plotting
- Support for different data types and conversion formulas

## Requirements

- .NET 7.0 or later
- Microsoft SQL Server (for signal metadata storage)
- Windows 10/11 with Visual Studio 2022

## Project Structure

- **A2L**: Contains the A2L file parser for extracting parameter information
- **DataAccess**: Database connectivity and signal metadata retrieval
- **Models**: Data models representing ECUs, signals, and readings
- **Services**: Services for parameter acquisition and XCP communication
- **ViewModels**: MVVM implementation for the user interface
- **XCP**: XCP protocol implementation for communicating with ECUs

## Setup

1. Clone the repository
2. Run the SQL script in the Database folder to create and populate the signal metadata database
3. Update the connection string in MainWindow.xaml.cs
4. Build and run the application

## Usage

1. Select an ECU from the dropdown menu
2. Click "Connect" to establish XCP connection
3. Browse available signals in the left panel
4. Add signals to the monitoring list
5. The graph will automatically update to show real-time values
6. Use the "Clear Plot" button to reset the graph display

## Simulation Mode

If a physical ECU connection is not available, the application will automatically fall back to simulation mode, which generates realistic-looking data for demonstration purposes.

## Libraries Used

- **OxyPlot**: For data visualization
- **Dapper**: For efficient database access
- **Microsoft.Data.SqlClient**: For SQL Server connectivity

## A2L File Support

The application includes a robust A2L parser that extracts:
- Measurement definitions (signals)
- Characteristic definitions (calibration parameters)
- Computation methods (conversion formulas)
- Memory layout information

## License

MIT

## Disclaimer

This is a demonstration application and might need adjustments for use in real automotive environments. Always follow safety protocols when connecting to automotive ECUs.
