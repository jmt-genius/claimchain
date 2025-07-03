import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/heart_rate_data.dart';

class FitbitService {
  static const String _clientId =
      'YOUR_FITBIT_CLIENT_ID'; // Replace with actual client ID
  static const String _clientSecret =
      'YOUR_FITBIT_CLIENT_SECRET'; // Replace with actual client secret
  static const String _redirectUri = 'claimchain://oauth/callback';
  static const String _authorizationUrl =
      'https://www.fitbit.com/oauth2/authorize';
  static const String _tokenUrl = 'https://api.fitbit.com/oauth2/token';
  static const String _apiBaseUrl = 'https://api.fitbit.com/1/user/-';

  String? _accessToken;
  String? _refreshToken;

  Future<bool> authenticate() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _accessToken = prefs.getString('fitbit_access_token');
      _refreshToken = prefs.getString('fitbit_refresh_token');

      if (_accessToken != null) {
        // Check if token is still valid
        final isValid = await _validateToken();
        if (isValid) return true;
      }

      // Perform OAuth2 flow
      final authUrl = Uri.parse(_authorizationUrl).replace(
        queryParameters: {
          'response_type': 'code',
          'client_id': _clientId,
          'redirect_uri': _redirectUri,
          'scope': 'heartrate',
          'expires_in': '604800', // 7 days
        },
      );

      // Launch the authorization URL
      if (await canLaunchUrl(authUrl)) {
        await launchUrl(authUrl, mode: LaunchMode.externalApplication);

        // Note: In a real app, you would need to handle the callback URL
        // This is a simplified version. For production, you'd need to:
        // 1. Set up a custom URL scheme handler
        // 2. Listen for the callback URL
        // 3. Extract the authorization code

        // For now, we'll simulate a successful authentication
        // In practice, you'd get the code from the callback URL
        print(
          'Please complete the OAuth flow in your browser and return to the app',
        );
        return false;
      }
    } catch (e) {
      print('Fitbit authentication error: $e');
    }
    return false;
  }

  Future<bool> _validateToken() async {
    try {
      final response = await http.get(
        Uri.parse('$_apiBaseUrl/profile.json'),
        headers: {'Authorization': 'Bearer $_accessToken'},
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<List<HeartRateData>> getHeartRateData() async {
    if (_accessToken == null) {
      final authenticated = await authenticate();
      if (!authenticated) return [];
    }

    try {
      final now = DateTime.now();
      final endTime = now.toUtc();
      final startTime = endTime.subtract(const Duration(minutes: 60));

      final response = await http.get(
        Uri.parse(
          '$_apiBaseUrl/activities/heart/date/${_formatDate(startTime)}/1d/1min.json',
        ),
        headers: {'Authorization': 'Bearer $_accessToken'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final activities = data['activities-heart-intraday']['dataset'] as List;

        return activities.map((activity) {
          final timeStr = activity['time'] as String;
          final dateTime = DateTime.parse('${_formatDate(startTime)} $timeStr');
          return HeartRateData(
            timestamp: dateTime,
            heartRate: activity['value'] as int,
          );
        }).toList();
      }
    } catch (e) {
      print('Error fetching heart rate data: $e');
    }
    return [];
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('fitbit_access_token');
    await prefs.remove('fitbit_refresh_token');
    _accessToken = null;
    _refreshToken = null;
  }
}
