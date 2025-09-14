# Food Safety Agency - User Accounts

This document contains all user accounts and their login credentials for the Food Safety Agency system.

## 🔐 Login URL
```
http://127.0.0.1:8000/login/
```

## 👥 User Accounts by Role

### 🔴 Super Administrators
Super admins have full system access including user management, settings, and all features.

| Name | Username | Password | Email |
|------|----------|----------|-------|
| Armand | `armand` | `Armand2025SuperAdmin` | armand@foodsafetyagency.com |
| Anthony | `anthony` | `Anthony2025SuperAdmin` | anthony@foodsafetyagency.com |

### 🟡 Administrators  
Administrators have most system access but limited user management.

| Name | Username | Password | Email |
|------|----------|----------|-------|
| Mpho | `mpho` | `Mpho2025Admin` | mpho@foodsafetyagency.com |

### 🧪 Lab Technicians (Scientists)
Lab technicians can only see inspections where samples were taken.

| Name | Username | Password | Email |
|------|----------|----------|-------|
| Christina | `christina` | `Christina2025LabTech` | christina@foodsafetyagency.com |

### 👮 Inspectors
Inspectors can only see their own inspections and have limited editing capabilities.

| Inspector Name | Username | Password | Inspector ID | Inspections |
|---------------|----------|----------|--------------|-------------|
| BEN VISAGIE | `benvisagie` | `BENVISAGIE202568` | 68 | 301 |
| CINGA NGONGO | `cingangongo` | `CINGANGONGO2025177` | 177 | 616 |
| GLADYS MANGANYE | `gladysmanganye` | `GLADYSMANGANYE2025188` | 188 | 541 |
| JOFRED STEYN | `jofredsteyn` | `JOFREDSTEYN2025153` | 153 | 276 |
| KUTLWANO KUNTWANE | `kutlwanokuntwane` | `KUTLWANOKUNTWANE2025186` | 186 | 302 |
| LWANDILE MAQINA | `lwandilemaqina` | `



























































































































































































































































































































































































































































































































































` | 174 | 530 |
| MOKGADI SELONE | `mokgadiselone` | `MOKGADISELONE2025143` | 143 | 246 |
| NELISA NTOYAPHI | `nelisantoyaphi` | `NELISANTOYAPHI2025196` | 196 | 373 |
| NEO NOE | `neonoe` | `NEONOE2025118` | 118 | 103 |
| PERCY MALEKA | `percymaleka` | `PERCYMALEKA2025185` | 185 | 495 |
| SANDISIWE DLISANI | `sandisiwedlisani` | `SANDISIWEDLISANI2025124` | 124 | 471 |
| THATO SEKHOTHO | `thatosekhotho` | `THATOSEKHOTHO2025166` | 166 | 469 |
| XOLA MPELUZA | `xolampeluza` | `XOLAMPELUZA2025184` | 184 | 507 |

### 🔧 Developer Accounts
Developer accounts have full system access including compliance document management.

| Name | Username | Password | Role | Email |
|------|----------|----------|------|-------|
| Ethan | `ethan` | `Ethan2025Developer` | developer | ethan@foodsafetyagency.com |
| Developer | `developer` | [Existing Password] | developer | - |
## 📋 Role Permissions

### 🔴 Super Admin (`super_admin`)
- ✅ Full system access
- ✅ User management (create, edit, delete users)
- ✅ System settings
- ✅ All inspections (view, edit, delete)
- ✅ Client management
- ✅ File uploads and downloads
- ✅ System logs
- ✅ Analytics and reports

### 🟡 Admin (`admin`)
- ✅ Most system access
- ✅ Limited user management
- ✅ All inspections (view, edit)
- ✅ Client management  
- ✅ File uploads and downloads
- ✅ System logs
- ✅ Analytics and reports
- ❌ Cannot delete inspections
- ❌ Limited system settings

### 👮 Inspector (`inspector`)
- ✅ View own inspections only
- ✅ Edit own inspection details
- ✅ Upload documents for own inspections
- ❌ Cannot see other inspectors' work
- ❌ No user management
- ❌ No system settings
- ❌ No client management

### 🧪 Scientist/Lab Technician (`scientist`)
- ✅ View inspections with samples only
- ✅ Edit lab-related fields
- ✅ Upload lab results
- ❌ Cannot see non-sampled inspections
- ❌ No user management
- ❌ Limited system access

### 🔧 Developer (`developer`)
- ✅ Full system access
- ✅ Compliance document management
- ✅ Performance monitoring
- ✅ System debugging tools
- ✅ All admin capabilities

## 🚀 Getting Started

1. **Go to**: http://127.0.0.1:8000/login/
2. **Enter credentials** from the tables above
3. **Access your role-specific features**

## 📧 System Logging

All user activities are logged in the System Logs, including:
- Login/logout events
- Sent status changes
- File uploads
- Data modifications
- User management actions

Access System Logs at: http://127.0.0.1:8000/system-logs/

## 🔄 Password Policy

- **Inspector passwords**: `InspectorName2025InspectorID`
- **Admin passwords**: `Name2025Role`
- **All passwords are case-sensitive**
- **No special characters in passwords for simplicity**

---
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
