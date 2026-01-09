#!/usr/bin/env python3
"""
Test script to upsert InspectorMapping entries from provided inspector list
Run with: python test_update_inspector_mappings.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import transaction
from main.models import InspectorMapping

# (inspector_id, is_active, first_name, last_name)
INSPECTORS = [
    (68, 1, 'BEN', 'VISAGIE'),
    (70, 1, 'THERESA', 'DIOGO'),
    (71, 1, 'PALESA', 'MPANA'),
    (72, 1, 'CHARMAINE', 'NEL'),
    (73, 0, 'RAM', 'RAMBURAN'),
    (74, 0, 'HEIN', 'NEL'),
    (75, 0, 'SIBONELO', 'ZONDI'),
    (76, 1, 'PETRUS', 'POOL'),
    (77, 1, 'DELAREY', 'RIBBENS'),
    (78, 1, 'DEWALD', 'KORF'),
    (79, 1, 'WENDY', 'CHAKA'),
    (80, 0, 'NIPHO', 'NGOMANE'),
    (81, 0, 'CHELESILE', 'MOYO'),
    (82, 1, 'JOE', 'ROSENBLATT'),
    (83, 0, 'SIMON', 'SWART'),
    (84, 1, 'ANDREAS', 'LETABA'),
    (85, 1, 'JOEL', 'MHANGWA'),
    (86, 1, 'ASISIPHO', 'LANDE'),
    (87, 1, 'LOUIS', 'VISAGIE'),
    (88, 0, 'RASSIE', 'SMIT'),
    (89, 1, 'NICOLE', 'BERGH'),
    (91, 0, 'MONTI', 'RAMAANO'),
    (92, 1, 'THABO', 'MAGWAZA'),
    (93, 1, 'VICTOR', 'MATHEBULA'),
    (94, 1, 'FRANCOIS', 'PRETORIUS'),
    (95, 1, 'EVANS', 'NKWINIKA'),
    (96, 1, 'MCAULEY', 'MUSUNDA'),
    (97, 1, 'NAKISANI', 'BALOYI'),
    (102, 0, 'ALI', 'MODIKOE'),
    (103, 1, 'GERRIT', 'PEKEMA'),
    (105, 0, 'CHRISTIAAN', 'WOLMARANS'),
    (106, 1, 'ARMAND', 'VISAGIE'),
    (113, 0, 'KATLEGO', 'MOKHUA'),
    (116, 1, 'FINANCE', 'TWO'),
    (118, 1, 'NEO', 'NOE'),
    (123, 0, 'LIZELLE', 'BREEDT'),
    (124, 1, 'SANDISIWE', 'DLISANI'),
    (125, 1, 'MARIUS', 'CARSTENS'),
    (126, 0, 'THAPELO', 'MAPOTSE'),
    (127, 0, 'THAPELO', 'MAPOTSE'),
    (131, 1, 'EDITH', 'SELEPE'),
    (132, 1, 'PAKI', 'OLIFANT'),
    (133, 1, 'CALVIN', 'CLAASSENS'),
    (140, 1, 'AGREEMENT', 'MOSIA'),
    (141, 1, 'IT', 'IT'),
    (142, 0, 'MARIANA', 'DU TOIT'),
    (143, 1, 'MOKGADI', 'SELONE'),
    (144, 1, 'VHAHANGWELE', 'RALULIMI'),
    (145, 0, 'WILSON', 'MAIFO'),
    (146, 1, 'ELIAS', 'THEKISO'),
    (147, 0, 'BRIAN', 'XULU'),
    (148, 1, 'COLLEN', 'DLAMINI'),
    (149, 1, 'THEMBA', 'SHABANGU'),
    (150, 1, 'CHRISNA', 'POOL'),
    (153, 1, 'JOFRED', 'STEYN'),
    (154, 1, 'SEUN', 'SEBOLAI'),
    (160, 0, 'LERATO', 'MODIBA'),
    (163, 1, 'DENNIS', 'CELE'),
    (164, 1, 'HENNIE', 'CHILOANE'),
    (166, 1, 'THATO', 'SEKHOTHO'),
    (173, 1, 'HLENGIWE', 'GUMEDE'),
    (174, 1, 'LWANDILE', 'MAQINA'),
    (175, 1, 'PETRUS', 'POOL'),
    (177, 1, 'CINGA', 'NGONGO'),
    (178, 1, 'NTABISENG', 'MASEKO'),
    (179, 1, 'KABELO', 'MOKGALAKA'),
    (183, 1, 'MPHO', 'MOTAUNG'),
    (184, 1, 'XOLA', 'MPELUZA'),
    (185, 1, 'PERCY', 'MALEKA'),
    (186, 1, 'KUTLWANO', 'KUNTWANE'),
    (187, 1, 'SIPHO', 'NDAMASE'),
    (188, 1, 'GLADYS', 'MANGANYE'),
    (194, 1, 'PHUMZILE', 'MASOMBUKA'),
    (196, 1, 'NELISA', 'NTOYAPHI'),
    (197, 1, 'HAZEL', 'SOSIBO'),
    (198, 1, 'BRITTNEY', 'PILLAY'),
    (202, 1, 'DIMAKATSO', 'MODIBA'),
    (203, 0, 'LEBO', 'SEKGOBANE'),
    (204, 1, 'CORNELIUS', 'ADAMS'),
]

def upsert_mappings():
    created = 0
    updated = 0
    with transaction.atomic():
        for inspector_id, is_active, first, last in INSPECTORS:
            name = f"{first.strip()} {last.strip()}".upper()
            obj, was_created = InspectorMapping.objects.update_or_create(
                inspector_id=inspector_id,
                defaults={
                    'inspector_name': name,
                    'is_active': bool(is_active),
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1
    return created, updated

if __name__ == "__main__":
    c, u = upsert_mappings()
    print(f"Inspector mappings upserted. Created={c}, Updated={u}")






