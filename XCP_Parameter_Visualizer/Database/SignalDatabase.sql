-- Signal Metadata Database Schema

-- Create database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SignalMetadata')
BEGIN
    CREATE DATABASE SignalMetadata;
END
GO

USE SignalMetadata;
GO

-- Create ECUs table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ECUs')
BEGIN
    CREATE TABLE ECUs (
        ECUId INT PRIMARY KEY IDENTITY(1,1),
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(255) NULL,
        A2LFilePath NVARCHAR(255) NOT NULL,
        XCPProtocol NVARCHAR(50) DEFAULT 'Ethernet' NOT NULL,
        IPAddress NVARCHAR(50) NULL,
        Port INT NULL,
        CANInterface NVARCHAR(50) NULL,
        CANId INT NULL
    );
END
GO

-- Create SignalGroups table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SignalGroups')
BEGIN
    CREATE TABLE SignalGroups (
        GroupId INT PRIMARY KEY IDENTITY(1,1),
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(255) NULL,
        ECUId INT FOREIGN KEY REFERENCES ECUs(ECUId)
    );
END
GO

-- Create Signals table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Signals')
BEGIN
    CREATE TABLE Signals (
        SignalId INT PRIMARY KEY IDENTITY(1,1),
        ECUId INT FOREIGN KEY REFERENCES ECUs(ECUId),
        GroupId INT FOREIGN KEY REFERENCES SignalGroups(GroupId) NULL,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(255) NULL,
        Address NVARCHAR(100) NULL,
        DataType NVARCHAR(50) NOT NULL,
        MinValue FLOAT NULL,
        MaxValue FLOAT NULL,
        Units NVARCHAR(50) NULL,
        Conversion NVARCHAR(255) NULL,
        IsCalibration BIT DEFAULT 0 NOT NULL,
        IsMeasurement BIT DEFAULT 1 NOT NULL
    );
END
GO

-- Insert sample data
-- Sample ECU
IF NOT EXISTS (SELECT * FROM ECUs WHERE Name = 'Engine_ECU')
BEGIN
    INSERT INTO ECUs (Name, Description, A2LFilePath, XCPProtocol, IPAddress, Port)
    VALUES ('Engine_ECU', 'Engine Control Unit', 'C:\Samples\Engine.a2l', 'Ethernet', '192.168.1.10', 5555);
END
GO

-- Sample Signal Group
IF NOT EXISTS (SELECT * FROM SignalGroups WHERE Name = 'Engine_Parameters')
BEGIN
    DECLARE @ECUId INT = (SELECT ECUId FROM ECUs WHERE Name = 'Engine_ECU');
    
    INSERT INTO SignalGroups (Name, Description, ECUId)
    VALUES ('Engine_Parameters', 'Engine Performance Parameters', @ECUId);
END
GO

-- Sample Signals
IF NOT EXISTS (SELECT * FROM Signals WHERE Name = 'EngineSpeed')
BEGIN
    DECLARE @ECUId INT = (SELECT ECUId FROM ECUs WHERE Name = 'Engine_ECU');
    DECLARE @GroupId INT = (SELECT GroupId FROM SignalGroups WHERE Name = 'Engine_Parameters');
    
    INSERT INTO Signals (ECUId, GroupId, Name, Description, Address, DataType, MinValue, MaxValue, Units, Conversion, IsMeasurement)
    VALUES 
        (@ECUId, @GroupId, 'EngineSpeed', 'Engine RPM', '0x01020304', 'UINT16', 0, 8000, 'RPM', 'X*1.0', 1),
        (@ECUId, @GroupId, 'ThrottlePosition', 'Throttle Position', '0x01020308', 'UINT8', 0, 100, '%', 'X*0.392157', 1),
        (@ECUId, @GroupId, 'EngineTemp', 'Engine Temperature', '0x01020310', 'INT16', -40, 215, '°C', 'X*0.01', 1),
        (@ECUId, @GroupId, 'ManifoldPressure', 'Intake Manifold Pressure', '0x01020314', 'UINT16', 0, 300, 'kPa', 'X*0.1', 1),
        (@ECUId, @GroupId, 'AirFuelRatio', 'Air-Fuel Ratio', '0x01020318', 'UINT16', 10, 20, ':1', 'X*0.001', 1),
        (@ECUId, @GroupId, 'IgnitionAdvance', 'Ignition Timing Advance', '0x0102031C', 'INT8', -20, 60, '°', 'X*0.5', 1),
        (@ECUId, @GroupId, 'FuelInjectionTime', 'Fuel Injection Time', '0x01020320', 'UINT16', 0, 25, 'ms', 'X*0.01', 1),
        (@ECUId, @GroupId, 'EngineTorque', 'Engine Torque', '0x01020324', 'UINT16', 0, 500, 'Nm', 'X*0.1', 1);
END
GO

-- Sample ECU 2
IF NOT EXISTS (SELECT * FROM ECUs WHERE Name = 'Transmission_ECU')
BEGIN
    INSERT INTO ECUs (Name, Description, A2LFilePath, XCPProtocol, IPAddress, Port)
    VALUES ('Transmission_ECU', 'Transmission Control Unit', 'C:\Samples\Transmission.a2l', 'Ethernet', '192.168.1.11', 5555);
END
GO

-- Sample Signal Group 2
IF NOT EXISTS (SELECT * FROM SignalGroups WHERE Name = 'Transmission_Parameters')
BEGIN
    DECLARE @ECUId INT = (SELECT ECUId FROM ECUs WHERE Name = 'Transmission_ECU');
    
    INSERT INTO SignalGroups (Name, Description, ECUId)
    VALUES ('Transmission_Parameters', 'Transmission Parameters', @ECUId);
END
GO

-- Sample Signals 2
IF NOT EXISTS (SELECT * FROM Signals WHERE Name = 'CurrentGear')
BEGIN
    DECLARE @ECUId INT = (SELECT ECUId FROM ECUs WHERE Name = 'Transmission_ECU');
    DECLARE @GroupId INT = (SELECT GroupId FROM SignalGroups WHERE Name = 'Transmission_Parameters');
    
    INSERT INTO Signals (ECUId, GroupId, Name, Description, Address, DataType, MinValue, MaxValue, Units, Conversion, IsMeasurement)
    VALUES 
        (@ECUId, @GroupId, 'CurrentGear', 'Current Gear Position', '0x02030405', 'UINT8', 0, 8, '-', 'X', 1),
        (@ECUId, @GroupId, 'TransmissionTemp', 'Transmission Oil Temperature', '0x02030410', 'INT16', -40, 200, '°C', 'X*0.01', 1),
        (@ECUId, @GroupId, 'ShiftTime', 'Time to Shift Gears', '0x02030418', 'UINT16', 0, 5000, 'ms', 'X', 1),
        (@ECUId, @GroupId, 'TorqueConverter', 'Torque Converter Slip', '0x02030420', 'UINT16', 0, 100, '%', 'X*0.1', 1),
        (@ECUId, @GroupId, 'OutputShaftSpeed', 'Output Shaft Speed', '0x02030428', 'UINT16', 0, 10000, 'RPM', 'X*0.5', 1);
END
GO
