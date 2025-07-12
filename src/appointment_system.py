"""
Appointment Management System for Intel AI Healthcare Kiosk
Handles appointment booking, scheduling, and video call integration
"""

import streamlit as st
import pandas as pd
import csv
import os
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any
import uuid
import logging

logger = logging.getLogger(__name__)

class AppointmentSystem:
    """
    Manages appointment booking and video call integration
    """
    
    def __init__(self):
        """Initialize the appointment system"""
        self.appointments_file = "data/appointments.csv"
        self.doctors_file = "data/doctors.csv"
        self.ensure_data_files()
        logger.info("Appointment System initialized")
    
    def ensure_data_files(self):
        """Ensure appointment and doctor data files exist"""
        os.makedirs("data", exist_ok=True)
        
        # Create appointments file if it doesn't exist
        if not os.path.exists(self.appointments_file):
            with open(self.appointments_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "appointment_id", "user_id", "user_name", "doctor_id", 
                    "doctor_name", "appointment_date", "appointment_time", 
                    "status", "meeting_link", "specialty", "notes", "created_at"
                ])
        
        # Create doctors file with sample data if it doesn't exist
        if not os.path.exists(self.doctors_file):
            with open(self.doctors_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "doctor_id", "name", "specialty", "available_days", 
                    "available_times", "meeting_platform", "meeting_room", "status"
                ])
                
                # Add sample doctors
                sample_doctors = [
                    ["DR001", "Dr. Rajesh Kumar", "General Physician", "Mon,Tue,Wed,Thu,Fri", "09:00-17:00", "zoom", "https://zoom.us/j/1234567890", "active"],
                    ["DR002", "Dr. Priya Sharma", "Cardiologist", "Mon,Wed,Fri", "10:00-16:00", "meet", "https://meet.google.com/abc-defg-hij", "active"],
                    ["DR003", "Dr. Suresh Patel", "Dermatologist", "Tue,Thu,Sat", "11:00-18:00", "zoom", "https://zoom.us/j/0987654321", "active"],
                    ["DR004", "Dr. Anita Singh", "Pediatrician", "Mon,Tue,Thu,Fri", "08:00-16:00", "meet", "https://meet.google.com/xyz-uvwx-rst", "active"],
                    ["DR005", "Dr. Vikram Reddy", "Neurologist", "Wed,Fri,Sat", "12:00-19:00", "zoom", "https://zoom.us/j/1122334455", "active"]
                ]
                
                for doctor in sample_doctors:
                    writer.writerow(doctor)
    
    def get_doctors(self) -> List[Dict]:
        """Get list of available doctors"""
        doctors = []
        try:
            with open(self.doctors_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['status'] == 'active':
                        doctors.append(row)
        except Exception as e:
            logger.error(f"Error reading doctors file: {e}")
        return doctors
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict]:
        """Get doctor information by ID"""
        doctors = self.get_doctors()
        for doctor in doctors:
            if doctor['doctor_id'] == doctor_id:
                return doctor
        return None
    
    def get_available_time_slots(self, doctor_id: str, date: datetime) -> List[str]:
        """Get available time slots for a doctor on a specific date"""
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return []
        
        # Check if doctor is available on this day
        day_name = date.strftime('%a')  # Mon, Tue, etc.
        available_days = doctor['available_days'].split(',')
        if day_name not in available_days:
            return []
        
        # Parse available times (format: "09:00-17:00")
        time_range = doctor['available_times']
        start_time_str, end_time_str = time_range.split('-')
        start_hour, start_min = map(int, start_time_str.split(':'))
        end_hour, end_min = map(int, end_time_str.split(':'))
        
        # Generate 30-minute time slots
        time_slots = []
        current_time = time(start_hour, start_min)
        end_time = time(end_hour, end_min)
        
        # For same-day appointments, start from current time + 1 hour buffer
        now = datetime.now()
        is_today = date.date() == now.date()
        
        if is_today:
            # Add 1 hour buffer for same-day appointments
            min_booking_time = (now + timedelta(hours=1)).time()
            if current_time < min_booking_time:
                # Round up to next 30-minute slot
                next_slot_hour = min_booking_time.hour
                next_slot_min = 30 if min_booking_time.minute > 0 else 0
                if next_slot_min == 30 and min_booking_time.minute > 30:
                    next_slot_hour += 1
                    next_slot_min = 0
                current_time = time(next_slot_hour, next_slot_min)
        
        while current_time < end_time:
            time_slots.append(current_time.strftime('%H:%M'))
            # Add 30 minutes
            dt = datetime.combine(datetime.today(), current_time)
            dt += timedelta(minutes=30)
            current_time = dt.time()
        
        # Filter out already booked slots
        booked_slots = self.get_booked_slots(doctor_id, date)
        available_slots = [slot for slot in time_slots if slot not in booked_slots]
        
        return available_slots
    
    def get_booked_slots(self, doctor_id: str, date: datetime) -> List[str]:
        """Get already booked time slots for a doctor on a specific date"""
        booked_slots = []
        try:
            with open(self.appointments_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (row['doctor_id'] == doctor_id and 
                        row['appointment_date'] == date.strftime('%Y-%m-%d') and
                        row['status'] in ['confirmed', 'pending']):
                        booked_slots.append(row['appointment_time'])
        except Exception as e:
            logger.error(f"Error reading appointments file: {e}")
        return booked_slots
    
    def book_appointment(self, user_id: str, user_name: str, doctor_id: str, 
                        appointment_date: str, appointment_time: str, notes: str = "") -> Dict:
        """Book a new appointment"""
        try:
            doctor = self.get_doctor_by_id(doctor_id)
            if not doctor:
                return {"success": False, "message": "Doctor not found"}
            
            appointment_id = str(uuid.uuid4())[:8].upper()
            
            # Create meeting link based on platform
            meeting_link = doctor['meeting_room']
            if doctor['meeting_platform'] == 'zoom':
                meeting_link = f"{doctor['meeting_room']}?pwd=healthcare123"
            
            # Save appointment
            with open(self.appointments_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    appointment_id, user_id, user_name, doctor_id,
                    doctor['name'], appointment_date, appointment_time,
                    'confirmed', meeting_link, doctor['specialty'], notes,
                    datetime.now().isoformat()
                ])
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "meeting_link": meeting_link,
                "doctor_name": doctor['name'],
                "message": "Appointment booked successfully!"
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {"success": False, "message": f"Error booking appointment: {str(e)}"}
    
    def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Get all appointments for a user"""
        appointments = []
        try:
            with open(self.appointments_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        appointments.append(row)
        except Exception as e:
            logger.error(f"Error reading user appointments: {e}")
        return sorted(appointments, key=lambda x: x['appointment_date'], reverse=True)
    
    def cancel_appointment(self, appointment_id: str, user_id: str) -> bool:
        """Cancel an appointment"""
        try:
            # Read all appointments
            appointments = []
            with open(self.appointments_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                appointments = list(reader)
            
            # Update the specific appointment
            updated = False
            for appointment in appointments:
                if (appointment['appointment_id'] == appointment_id and 
                    appointment['user_id'] == user_id):
                    appointment['status'] = 'cancelled'
                    updated = True
                    break
            
            if updated:
                # Write back all appointments
                with open(self.appointments_file, 'w', newline='') as f:
                    if appointments:
                        writer = csv.DictWriter(f, fieldnames=appointments[0].keys())
                        writer.writeheader()
                        writer.writerows(appointments)
                return True
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
        return False
