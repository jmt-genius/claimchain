# Claimchain - Heart Rate Monitoring App

A Flutter application that monitors heart rate and detects cardiac activity in two modes: Simulation and Live.

## Features

- **Simulation Mode**: Generates artificial heart rate spikes to simulate cardiac events
- **Live Mode**: Connects to Fitbit API using OAuth2 authentication for real-time heart rate monitoring
- **Cardiac Spike Detection**: Detects heart rate spikes (>130 BPM with >40 BPM increase from baseline)
- **Real-time Charts**: Displays heart rate trends using fl_chart
- **Local Storage**: Stores cardiac events using SQLite database
- **Server Sync**: Syncs detected events to backend server
- **Modern UI**: Clean, mobile-friendly interface with soft colors and card layouts

## Prerequisites

- Flutter 3.x or higher
- Dart SDK with null safety
- Android Studio / VS Code with Flutter extensions
- Fitbit Developer Account (for Live mode)

## Setup Instructions

### 1. Install Dependencies

```bash
flutter pub get
```

### 2. Configure Fitbit API (for Live Mode)

1. Create a Fitbit Developer account at [https://dev.fitbit.com/](https://dev.fitbit.com/)
2. Create a new app in the Fitbit Developer Console
3. Note your Client ID and Client Secret
4. Set the OAuth 2.0 Redirect URI to: `claimchain://oauth/callback`

### 3. Update Configuration

Edit `lib/services/fitbit_service.dart` and replace:
- `YOUR_FITBIT_CLIENT_ID` with your actual Fitbit Client ID
- `YOUR_FITBIT_CLIENT_SECRET` with your actual Fitbit Client Secret

Edit `lib/services/api_service.dart` and replace:
- `https://your-backend-api.com` with your actual backend API URL

### 4. Run the Application

```bash
flutter run
```

## Usage

### Simulation Mode
- Toggle to "Simulation" mode
- Click "Start Monitoring" to begin generating artificial heart rate data
- The app will occasionally generate spikes to simulate cardiac events
- Watch for the "⚠️ Cardiac Spike Detected" alert

### Live Mode
- Toggle to "Live" mode
- Click "Start Monitoring" to authenticate with Fitbit
- Complete the OAuth2 flow in your browser
- The app will fetch real heart rate data from your Fitbit device
- Monitor for real cardiac events

### Features
- **Real-time Heart Rate Display**: Shows current heart rate with color-coded indicators
- **Heart Rate Chart**: Displays the last 60 seconds of heart rate data
- **Event Detection**: Automatically detects and stores cardiac spikes
- **Sync to Server**: Push detected events to your backend server
- **Event History**: View details of the most recent cardiac event

## Architecture

### State Management
- Uses Provider pattern for state management
- Clean separation between UI, state, and storage layers

### Database
- SQLite database using sqflite package
- Stores only the most recent cardiac event
- Includes customer ID, timestamp, heart rate, mode, and summary

### API Integration
- Fitbit OAuth2 authentication
- REST API calls for heart rate data
- HTTP client for server synchronization

### UI Components
- Material Design 3 with custom theming
- Responsive card-based layout
- Real-time chart updates
- Color-coded heart rate indicators

## File Structure

```
lib/
├── main.dart                 # App entry point
├── models/
│   ├── cardiac_event.dart    # Cardiac event data model
│   └── heart_rate_data.dart  # Heart rate data point model
├── providers/
│   └── heart_rate_provider.dart  # State management
├── screens/
│   └── home_screen.dart      # Main app screen
├── services/
│   ├── api_service.dart      # Backend API integration
│   ├── database_service.dart # SQLite database operations
│   ├── fitbit_service.dart   # Fitbit API integration
│   └── heart_rate_monitor.dart # Heart rate monitoring logic
└── widgets/
    └── heart_rate_chart.dart # Chart widget
```

## Dependencies

- `provider`: State management
- `sqflite`: SQLite database
- `fl_chart`: Heart rate charts
- `http`: HTTP client for API calls
- `flutter_web_auth`: OAuth2 authentication
- `shared_preferences`: Token storage
- `intl`: Date formatting

## Cardiac Event Detection Logic

The app detects cardiac spikes when:
- Heart rate > 130 BPM
- Spike increase > 40 BPM from previous reading
- Event is stored with timestamp, heart rate value, mode, and summary

## Backend API Format

When syncing to server, the app sends a POST request with JSON body:

```json
{
  "customerId": "user_123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "heartRate": 150,
  "mode": "simulation",
  "summary": "high-risk cardiac spike detected during simulation"
}
```

## Troubleshooting

### Common Issues

1. **Fitbit Authentication Fails**
   - Verify Client ID and Secret are correct
   - Check redirect URI matches exactly
   - Ensure app has heartrate scope

2. **Chart Not Displaying**
   - Ensure fl_chart dependency is installed
   - Check heart rate data is being generated

3. **Database Errors**
   - Verify sqflite dependency is installed
   - Check app permissions for storage

4. **Server Sync Fails**
   - Verify backend API URL is correct
   - Check network connectivity
   - Ensure backend accepts the JSON format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
