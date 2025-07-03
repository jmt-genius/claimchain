class HeartRateData {
  final DateTime timestamp;
  final int heartRate;

  HeartRateData({required this.timestamp, required this.heartRate});

  Map<String, dynamic> toJson() {
    return {'timestamp': timestamp.toIso8601String(), 'heartRate': heartRate};
  }

  factory HeartRateData.fromJson(Map<String, dynamic> json) {
    return HeartRateData(
      timestamp: DateTime.parse(json['timestamp']),
      heartRate: json['heartRate'],
    );
  }
}
