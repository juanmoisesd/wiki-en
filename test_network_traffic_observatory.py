#!/usr/bin/env python3
"""
Unit Test Suite for Network Traffic Observatory (Windows 10 x64 Native API Monitor)
===================================================================================
Tests core capabilities:
- Native API & mock network table polling
- Connection lifecycle: Active vs Historical transition
- Observed vs Estimated byte traffic tagging
- Non-judgmental remote destination classification
- Process ID to process name/path mapping
- Query filters (protocol, app name, status, remote IP, port, duration)
- CSV and JSON report export formatting and IP anonymization
"""

import unittest
import os
import json
import csv
import tempfile
from datetime import datetime
from network_traffic_observatory import (
    NetworkTrafficObservatory,
    Win32NetworkProvider,
    ConnectionRecord,
    classify_destination,
    anonymize_ip
)

class TestNetworkTrafficObservatory(unittest.TestCase):

    def setUp(self):
        self.provider = Win32NetworkProvider(force_mock=True)
        self.observatory = NetworkTrafficObservatory(provider=self.provider)

        # Mock sample connections
        self.sample_batch_1 = [
            {
                "protocol": "TCP",
                "local_address": "192.168.1.50:52134",
                "local_ip": "192.168.1.50",
                "local_port": 52134,
                "remote_address": "93.184.216.34:443",
                "remote_ip": "93.184.216.34",
                "remote_port": 443,
                "pid": 1024,
                "process_name": "chrome.exe",
                "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "state": "ESTABLISHED",
                "bytes_in": 1500,
                "bytes_out": 400,
                "is_observed": True
            },
            {
                "protocol": "UDP",
                "local_address": "0.0.0.0:5353",
                "local_ip": "0.0.0.0",
                "local_port": 5353,
                "remote_address": "*:*",
                "remote_ip": "*",
                "remote_port": 0,
                "pid": 800,
                "process_name": "svchost.exe",
                "process_path": "C:\\Windows\\System32\\svchost.exe",
                "state": "NONE",
                "bytes_in": 200,
                "bytes_out": 200,
                "is_observed": False
            }
        ]

    def test_destination_classification_non_judgmental(self):
        """Verify that unknown/unresolved destinations are non-judgmentally classified."""
        res_pub = classify_destination("192.0.2.1")  # TEST-NET-1 IP to prevent DNS network delays
        self.assertFalse(res_pub["is_local"])
        self.assertNotIn("malicious", res_pub["category"].lower())
        self.assertNotIn("threat", res_pub["description"].lower())

        res_local = classify_destination("192.168.1.1")
        self.assertTrue(res_local["is_local"])
        self.assertEqual(res_local["category"], "Private LAN Network")

        res_loopback = classify_destination("127.0.0.1")
        self.assertTrue(res_loopback["is_local"])
        self.assertEqual(res_loopback["category"], "Loopback / Localhost")

    def test_ip_anonymization(self):
        """Verify IP anonymization functionality."""
        self.assertEqual(anonymize_ip("192.168.1.50"), "192.168.1.xxx")
        self.assertEqual(anonymize_ip("127.0.0.1"), "127.0.0.1")
        self.assertEqual(anonymize_ip("*"), "*")

    def test_connection_lifecycle_active_vs_historical(self):
        """Verify transition between ACTIVE and HISTORICAL state when connection disappears."""
        self.observatory.poll(simulated_sample=self.sample_batch_1)

        # Confirm 2 active connections
        active_conns = self.observatory.query(status="ACTIVE")
        self.assertEqual(len(active_conns), 2)

        # Batch 2: Chrome connection closes (disappears)
        sample_batch_2 = [self.sample_batch_1[1]]  # Only svchost remains
        self.observatory.poll(simulated_sample=sample_batch_2)

        active_conns = self.observatory.query(status="ACTIVE")
        hist_conns = self.observatory.query(status="HISTORICAL")

        self.assertEqual(len(active_conns), 1)
        self.assertEqual(active_conns[0].process_name, "svchost.exe")
        self.assertEqual(len(hist_conns), 1)
        self.assertEqual(hist_conns[0].process_name, "chrome.exe")

    def test_observed_vs_estimated_bytes(self):
        """Verify distinction between observed vs estimated byte measurements."""
        self.observatory.poll(simulated_sample=self.sample_batch_1)
        records = self.observatory.query(app="chrome")
        self.assertEqual(len(records), 1)
        chrome_rec = records[0]

        self.assertEqual(chrome_rec.bytes_in_observed, 1500)
        self.assertEqual(chrome_rec.bytes_out_observed, 400)
        self.assertFalse(chrome_rec.is_byte_estimation)

        udp_records = self.observatory.query(app="svchost")
        self.assertEqual(len(udp_records), 1)
        svc_rec = udp_records[0]

        self.assertEqual(svc_rec.bytes_in_estimated, 200)
        self.assertEqual(svc_rec.bytes_out_estimated, 200)

    def test_query_filtering(self):
        """Verify query filters by protocol, app, remote IP, and port."""
        self.observatory.poll(simulated_sample=self.sample_batch_1)

        tcp_res = self.observatory.query(protocol="TCP")
        self.assertEqual(len(tcp_res), 1)
        self.assertEqual(tcp_res[0].protocol, "TCP")

        udp_res = self.observatory.query(protocol="UDP")
        self.assertEqual(len(udp_res), 1)
        self.assertEqual(udp_res[0].protocol, "UDP")

        app_res = self.observatory.query(app="chrome")
        self.assertEqual(len(app_res), 1)

        ip_res = self.observatory.query(remote_ip="93.184.216.34")
        self.assertEqual(len(ip_res), 1)

        port_res = self.observatory.query(port=443)
        self.assertEqual(len(port_res), 1)

    def test_app_activity_summary(self):
        """Verify application aggregate summary generation."""
        self.observatory.poll(simulated_sample=self.sample_batch_1)
        summary = self.observatory.get_app_activity_summary()

        self.assertIn("chrome.exe", summary)
        self.assertIn("svchost.exe", summary)
        self.assertEqual(summary["chrome.exe"]["bytes_in_observed"], 1500)
        self.assertEqual(summary["svchost.exe"]["bytes_in_estimated"], 200)

    def test_csv_export(self):
        """Verify CSV export format and contents."""
        self.observatory.poll(simulated_sample=self.sample_batch_1)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.observatory.export_csv(tmp_path, anonymize=True)
            self.assertTrue(os.path.exists(tmp_path))

            with open(tmp_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 2)
                # Verify anonymized remote IP
                chrome_row = [r for r in rows if r["process_name"] == "chrome.exe"][0]
                self.assertEqual(chrome_row["remote_ip"], "93.184.216.xxx")
                self.assertEqual(chrome_row["measurement_type"], "OBSERVED")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_json_export(self):
        """Verify JSON export structure, metadata, and app summaries."""
        self.observatory.poll(simulated_sample=self.sample_batch_1)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.observatory.export_json(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))

            with open(tmp_path, mode='r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertIn("metadata", data)
                self.assertIn("app_activity_summary", data)
                self.assertIn("connections", data)
                self.assertEqual(len(data["connections"]), 2)
                self.assertIn("chrome.exe", data["app_activity_summary"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()
