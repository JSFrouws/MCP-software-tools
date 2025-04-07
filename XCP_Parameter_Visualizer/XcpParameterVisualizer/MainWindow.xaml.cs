using System.Windows;
using XcpParameterVisualizer.ViewModels;

namespace XcpParameterVisualizer
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            
            // Configure connection string for your database
            string connectionString = "Server=localhost;Database=SignalMetadata;Trusted_Connection=True;TrustServerCertificate=True;";
            
            DataContext = new MainViewModel(connectionString);
        }
    }
}
