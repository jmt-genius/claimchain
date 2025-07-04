import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/heart_rate_provider.dart';
import '../widgets/heart_rate_chart.dart';
import 'range_simulation_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Claimchain',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: Colors.red.shade700,
        elevation: 0,
        actions: [
          Consumer<HeartRateProvider>(
            builder: (context, provider, child) {
              if (!provider.isSimulationMode) {
                // Secret camouflaged white button
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => const RangeSimulationScreen(),
                        ),
                      );
                    },
                    child: Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(
                          0.01,
                        ), // nearly invisible
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.white.withOpacity(0.05),
                        ),
                      ),
                    ),
                  ),
                );
              } else {
                return const SizedBox.shrink();
              }
            },
          ),
        ],
      ),
      body: Consumer<HeartRateProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            child: Column(
              children: [
                _buildModeToggleCard(provider),
                _buildHeartRateDisplay(provider),
                HeartRateChart(
                  heartRateHistory: provider.heartRateHistory,
                  currentHeartRate: provider.currentHeartRate,
                ),
                _buildLatestEventCard(provider),
                _buildCustomerIdCard(provider),
                _buildControlButtons(provider),
                if (provider.syncStatus.isNotEmpty)
                  _buildSyncStatusCard(provider),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildModeToggleCard(HeartRateProvider provider) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Monitoring Mode',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Switch(
              value: !provider.isSimulationMode,
              onChanged: (value) => provider.toggleMode(),
              activeColor: Colors.red.shade700,
            ),
            Text(
              provider.isSimulationMode ? 'Simulation' : 'Live',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: provider.isSimulationMode ? Colors.orange : Colors.green,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeartRateDisplay(HeartRateProvider provider) {
    final heartRate = provider.currentHeartRate;
    final isHigh = heartRate > 130;

    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: isHigh
                ? [Colors.red.shade100, Colors.orange.shade100]
                : [Colors.green.shade100, Colors.blue.shade100],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          children: [
            Text(
              'Current Heart Rate',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.favorite,
                  size: 40,
                  color: isHigh ? Colors.red : Colors.green,
                ),
                const SizedBox(width: 16),
                Text(
                  '$heartRate',
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: isHigh ? Colors.red.shade700 : Colors.green.shade700,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'BPM',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
            if (isHigh) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.red.shade100,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.red.shade300),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.warning, color: Colors.red, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '⚠️ Cardiac Spike Detected',
                      style: TextStyle(
                        color: Colors.red.shade700,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLatestEventCard(HeartRateProvider provider) {
    final event = provider.latestEvent;

    if (event == null) {
      return Card(
        elevation: 4,
        margin: const EdgeInsets.all(16),
        child: const Padding(
          padding: EdgeInsets.all(16),
          child: Text(
            'No cardiac events detected yet',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
        ),
      );
    }

    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Latest Detection',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildEventDetail('Mode', event.mode),
            _buildEventDetail('Heart Rate', '${event.heartRate} BPM'),
            _buildEventDetail('Time', _formatDateTime(event.timestamp)),
            _buildEventDetail('Summary', event.summary),
          ],
        ),
      ),
    );
  }

  Widget _buildEventDetail(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCustomerIdCard(HeartRateProvider provider) {
    final controller = TextEditingController(text: provider.customerId);
    final hasEvent = provider.latestEvent != null;

    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Customer ID',
                border: OutlineInputBorder(),
                hintText: 'Enter customer ID',
              ),
              onChanged: (value) => provider.setCustomerId(value),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: hasEvent ? () => provider.syncToServer() : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: Text(
                hasEvent
                    ? 'Sync Latest Cardiac Event'
                    : 'Waiting for Cardiac Event',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            if (!hasEvent) ...[
              const SizedBox(height: 8),
              const Text(
                'No cardiac events detected yet. Events are triggered when heart rate exceeds 130 BPM.',
                style: TextStyle(color: Colors.grey, fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildControlButtons(HeartRateProvider provider) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton(
              onPressed: () {
                if (provider.isMonitoring) {
                  provider.stopMonitoring();
                } else {
                  provider.startMonitoring();
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: provider.isMonitoring
                    ? Colors.red
                    : Colors.green,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                provider.isMonitoring ? 'Stop Monitoring' : 'Start Monitoring',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: provider.latestEvent != null
                  ? provider.syncToServer
                  : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                'Sync to Server',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSyncStatusCard(HeartRateProvider provider) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Icon(
              provider.syncStatus.contains('✅')
                  ? Icons.check_circle
                  : Icons.error,
              color: provider.syncStatus.contains('✅')
                  ? Colors.green
                  : Colors.red,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                provider.syncStatus,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: provider.syncStatus.contains('✅')
                      ? Colors.green
                      : Colors.red,
                ),
              ),
            ),
            IconButton(
              onPressed: provider.clearSyncStatus,
              icon: const Icon(Icons.close),
              iconSize: 16,
            ),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')} ${dateTime.day}/${dateTime.month}/${dateTime.year}';
  }
}
