# 🚗 AI Garage Management System

An AI-powered Garage & Vehicle Service Management ERP built on **Odoo 16** with **WhatsApp notifications** via Twilio.

> Built for Sri Lanka's vehicle service industry — solving a real, undigitized problem.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🚘 Vehicle Management | Register vehicles with owner, brand, model, fuel type |
| 📋 Job Cards | Full service order workflow with status tracking |
| 🔧 Parts Inventory | Track parts used per job, linked to Odoo products |
| 🤖 AI Service Reminders | Predict next service date based on usage patterns |
| 📱 WhatsApp Notifications | Auto-notify customers via Twilio API |
| 📊 Service History | Complete per-vehicle service timeline |
| 🧾 Invoice Generation | One-click invoice from job card |

---

## 🏗️ Project Structure

```
garage-erp/
├── custom_addons/
│   ├── garage_management/
│   │   ├── models/
│   │   │   ├── vehicle.py          # Vehicle records
│   │   │   ├── service_order.py    # Job cards + lines
│   │   │   ├── service_history.py  # History tracking
│   │   │   └── reminder.py         # AI reminder engine
│   │   ├── views/                  # XML UI definitions
│   │   ├── data/                   # Sequence data
│   │   ├── security/               # Access control
│   │   └── __manifest__.py
│   └── garage_whatsapp/
│       ├── models/
│       │   └── whatsapp.py         # Twilio integration
│       ├── views/
│       ├── security/
│       └── __manifest__.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/manojasomarathna/AI-Garage-Management-System.git
cd AI-Garage-Management-System
```

### 2. Start with Docker
```bash
docker-compose up -d
```

### 3. Open Odoo
```
URL:      http://localhost:8069
Database: garage_erp
```

### 4. Install Modules
- Go to **Apps** → Search `Garage`
- Install **Garage Management System**
- Install **Garage WhatsApp Notifications**

---

## 🤖 AI Reminder Logic

```python
# Prediction based on vehicle type + usage pattern
SERVICE_INTERVALS = {
    'car':   {'days': 90,  'km': 5000},
    'truck': {'days': 45,  'km': 3000},
    ...
}

# Adjusts interval based on estimated daily km:
# > 80 km/day  → 25% earlier service
# < 20 km/day  → 25% later service
```

A scheduled cron job runs daily to:
1. Generate reminders for all vehicles
2. Send WhatsApp notifications 7 days before predicted service date

---

## 📱 WhatsApp Setup (Twilio)

1. Sign up at [twilio.com](https://www.twilio.com) (free trial available)
2. Get your **Account SID** and **Auth Token**
3. Enable **WhatsApp Sandbox** in Twilio Console
4. In Odoo → **Garage → WhatsApp Settings** → Enter credentials

---

## 🔄 Job Card Workflow

```
Received → In Progress → Quality Check → Ready for Pickup → Delivered
```
- WhatsApp sent automatically when status → **Ready for Pickup**
- Service history auto-created on completion
- One-click invoice generation

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Odoo 16 ORM
- **Database**: PostgreSQL 15
- **Notifications**: Twilio WhatsApp API
- **Deployment**: Docker & Docker Compose

---

## 👨‍💻 Author

**Manoja Somarathna**
- GitHub: [@manojasomarathna](https://github.com/manojasomarathna)

---

## 📄 License

LGPL-3.0
