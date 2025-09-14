#!/usr/bin/env python3
"""
Create InspectorMapping records from the provided inspector list
This maps unique inspector IDs to their names without creating user accounts
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def create_inspector_mappings():
    """Create InspectorMapping records from the provided list"""
    print("🔗 Creating Inspector Mappings from List")
    print("=" * 80)
    
    from main.models import InspectorMapping
    import re
    
    # Inspector data from your list
    inspector_data = [
        (1, "ADMINISTRATOR", "ADMINISTRATOR"),
        (2, "DIRK", "VAN DEN BERG"),
        (3, "Susan", "von Wielligh"),
        (6, "ANDRE", "ERASMUS"),
        (11, "CALLIA", "OLIVIER"),
        (12, "KOBELA", "KEEPILE"),
        (13, "KAMO", "LEBURU"),
        (14, "NDZUDZENI", "MADIA"),
        (15, "TUMI", "MAPUDI"),
        (16, "CLIFORD", "MASHIANA"),
        (17, "COLLEN", "MASIYA"),
        (18, "DIMAKATSU", "MOILOA"),
        (19, "GLORIA", "MONAMA"),
        (20, "CASWELL", "BALE"),
        (21, "FRANS", "MONYAMANE"),
        (22, "JIM", "BAPELA"),
        (23, "NONYAMEZELO", "MADONSELA"),
        (24, "NICCO", "MATJABELA"),
        (25, "RAYMOND", "SELEBALO"),
        (26, "LAZOLA", "SOTHONDOSHE"),
        (27, "SIYAMTHANDA", "TYOBEKA"),
        (29, "WINFRED", "VAN WYK"),
        (30, "BRANDON", "BARON"),
        (31, "NOLUBABALO", "GOTSHANA"),
        (32, "ASHANTE", "HANSEN"),
        (33, "SOMELEZE", "JALI"),
        (34, "PIERRE", "JANSE VAN VUUREN"),
        (35, "SIBONOKUHLE", "KONYASHE"),
        (36, "NICCO", "MATHABELA"),
        (37, "STHEMBISO", "CELE"),
        (38, "PRISCILLA", "MANCIYA"),
        (39, "SIPHO", "ZWANE"),
        (40, "MARTIN", "SETSHWANE"),
        (41, "TSHEPO", "SEATLHUDI"),
        (42, "TUPPIE", "TUBB"),
        (43, "ANELE", "SOTYHANTYA"),
        (44, "KHAYALETU", "TUSWA"),
        (45, "BRAAM", "MAREE"),
        (46, "ZAMA", "NYATI"),
        (47, "KOBIE", "DU PREEZ"),
        (48, "NEVILLE", "HEN BOISEN"),
        (49, "ARTWELL", "MAVUSO"),
        (50, "DOROTHY", "MBELE"),
        (51, "JABULANI", "MOLEFE"),
        (52, "LERATO", "MASOMBUKA"),
        (53, "NDZUDZENI", "MADIA"),
        (54, "NOKUBONGA", "MATSHONA"),
        (55, "JOE", "SOAP TEST"),
        (56, "TSHEPO", "SEATLHUDI"),
        (57, "NELISA", "MABALI"),
        (58, "ANTON", "NONE"),
        (59, "MART - MARI", "VAN DALEN"),
        (60, "SANELE", "KHANYILE"),
        (61, "JEAN-MARI", "JORDAAN"),
        (62, "ELSIE", "APHANE"),
        (63, "ALFRED", "MOLOTO"),
        (64, "LONDIWE", "KHWELA"),
        (65, "ZANYA", "MOSTERT"),
        (66, "BELLA", "VAN VUUREN"),
        (67, "ANJA", "SWARTS"),
        (68, "BEN", "VISAGIE"),
        (69, "AFS", "DUMMY"),
        (70, "THERESA", "DIOGO"),
        (71, "PALESA", "MPANA"),
        (72, "CHARMAINE", "NEL"),
        (73, "RAM", "RAMBURAN"),
        (74, "HEIN", "NEL"),
        (75, "SIBONELO", "ZONDI"),
        (76, "PETRUS", "POOL"),
        (77, "DELAREY", "RIBBENS"),
        (78, "DEWALD", "KORF"),
        (79, "WENDY", "CHAKA"),
        (80, "NIPHO", "NGOMANE"),
        (81, "CHELESILE", "MOYO"),
        (82, "JOE", "ROSENBLATT"),
        (83, "SIMON", "SWART"),
        (84, "ANDREAS", "LETABA"),
        (85, "JOEL", "MHANGWA"),
        (86, "ASISIPHO", "LANDE"),
        (87, "LOUIS", "VISAGIE"),
        (88, "RASSIE", "SMIT"),
        (89, "NICOLE", "BERGH"),
        (90, "Spare1", "Spare2"),
        (91, "MONTI", "RAMAANO"),
        (92, "THABO", "MAGWAZA"),
        (93, "VICTOR", "MATHEBULA"),
        (94, "FRANCOIS", "PRETORIUS"),
        (95, "EVANS", "NKWINIKA"),
        (96, "MCAULEY", "MUSUNDA"),
        (97, "NAKISANI", "BALOYI"),
        (98, "PLACEHOLDER", "PLACEHOLDER"),
        (99, "TEST", "GMAIL"),
        (100, "RORISANG", "SHWENI"),
        (101, "SIHLE", "NKOSI"),
        (102, "ALI", "MODIKOE"),
        (103, "GERRIT", "PEKEMA"),
        (104, "MILICENT", "MASHA"),
        (105, "CHRISTIAAN", "WOLMARANS"),
        (106, "ARMAND", "VISAGIE"),
        (107, "DRIKUS", "GROENEWALD"),
        (108, "ETIENNE", "BOOYENS"),
        (110, "NELISIWE", "MASILELA"),
        (111, "DUMMY", "TESTER"),
        (112, "TESTER", "MOKHUA"),
        (113, "FINANCE", "PLACEHOLDER"),
        (114, "KHOTATSO", "PERSON"),
        (115, "NEO", "TWO"),
        (116, "TESTER", "MOLEFE"),
        (117, "YANELISA", "NOE"),
        (118, "ANJA", "TESTER"),
        (119, "Spare", "GOLOZELENI"),
        (120, "LIZELLE", "SWARTS"),
        (121, "SANDISIWE", "Spare"),
        (122, "MARIUS", "BREEDT"),
        (123, "THAPELO", "DLISANI"),
        (124, "THAPELO", "CARSTENS"),
        (125, "VICTOR", "MAPOTSE"),
        (126, "PROKON", "MAPOTSE"),
        (127, "TEST", "PHALANNDWA"),
        (128, "EDITH", "EMAIL"),
        (129, "PAKI", "USER"),
        (130, "CALVIN", "SELEPE"),
        (131, "ARMAND", "OLIFANT"),
        (132, "ERNEST", "CLAASSENS"),
        (133, "NTSHELE", "VISAGIE"),
        (134, "KGOTHATSO", "NONE"),
        (135, "EDWIN", "MASHISHI"),
        (136, "STANLEY", "MOHAPI"),
        (137, "AGREEMENT", "MOULDER"),
        (138, "IT", "ROOS"),
        (139, "MARIANA", "MOSIA"),
        (140, "MOKGADI", "IT"),
        (141, "VHAHANGWELE", "DU TOIT"),
        (142, "WILSON", "SELONE"),
        (143, "ELIAS", "RALULIMI"),
        (144, "BRIAN", "MAIFO"),
        (145, "COLLEN", "THEKISO"),
        (146, "THEMBA", "XULU"),
        (147, "CHRISNA", "DLAMINI"),
        (148, "NAAS", "SHABANGU"),
        (149, "PHINDILE", "POOL"),
        (150, "JOFRED", "TERBLANCHE"),
        (151, "SEUN", "JULE"),
        (152, "CLEMENT", "STEYN"),
        (153, "SANDILE", "SEBOLAI"),
        (154, "SANDILE", "DANKURU"),
        (155, "SANDILE", "KHANYILE"),
        (156, "SANDILE", "KHANYILE"),
        (157, "LERATO", "KHANYILE"),
        (158, "THOMAS", "KHANYILE"),
        (159, "SUSAN", "MODIBA"),
        (160, "DENNIS", "NDLOVU"),
        (161, "HENNIE", "MASEMOLA"),
        (162, "TERRANCE", "CELE"),
        (163, "THATO", "CHILOANE"),
        (164, "MAKGABO", "BROWN"),
        (165, "FRANCO", "SEKHOTHO"),
        (166, "NTHABASENG", "MASWINYANE"),
        (167, "DEBBIE", "STRYDOM"),
        (168, "MARNUS", "HATA"),
        (169, "DESMOND", "DE WET"),
        (170, "HLENGIWE", "BADENHORST"),
        (171, "LWANDILE", "MAKWATA"),
        (172, "PETRUS", "GUMEDE"),
        (173, "SANELE", "MAQINA"),
        (174, "CINGA", "POOL"),
        (175, "NTABISENG", "NDLOVUS"),
        (176, "KABELO", "NGONGO"),
        (177, "AUBREY", "MASEKO"),
        (178, "LESEGO", "MOKGALAKA"),
        (179, "FANIE", "DIBILWANA"),
        (180, "MPHO", "MOTSEMME"),
        (181, "XOLA", "MALATJIE"),
        (182, "PERCY", "MOTAUNG"),
        (183, "KUTLWANO", "MPELUZA"),
        (184, "SIPHO", "MALEKA"),
        (185, "GLADYS", "KUNTWANE"),
        (186, "PORTIA", "NDAMASE"),
        (187, "TOMMY", "MANGANYE"),
        (188, "NOMFUNDU", "SOMTUMANE"),
        (189, "NOMTHANDAZO", "SHANDU"),
        (190, "ANTHONY", "NCGOBO"),
        (191, "PHUMZILE", "MNCUBE"),
        (192, "OLIVIA", "PENZES"),
        (193, "NELISA", "MASOMBUKA"),
        (194, "HAZEL", "MARIRI"),
        (195, "BRITTNEY", "NTOYAPHI"),
        (196, "ETHAN", "SOSIBO"),
        (197, "ETHAN", "PILLAY"),
        (198, "SIMPHIWE", "SEVENSTER"),
        (199, "DIMAKATSO", "SEVENSTER"),
        (200, "LEBO", "MATHENJWA"),
        (201, "CORNELIUS", "MODIBA"),
        (202, "SEKGOBANE", "ADAMS"),
    ]
    
    print(f"📊 Processing {len(inspector_data)} inspector mappings\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for inspector_id, first_name, last_name in inspector_data:
        try:
            # Create full name
            full_name = f"{first_name} {last_name}".strip()
            
            # Clean the name for display
            clean_name = re.sub(r'[^a-zA-Z0-9\s\-]', '', full_name)
            
            # Check if mapping already exists
            try:
                mapping = InspectorMapping.objects.get(inspector_id=inspector_id)
                # Update existing mapping
                mapping.inspector_name = clean_name
                mapping.is_active = True
                mapping.save()
                updated_count += 1
                print(f"🔄 Updated: ID {inspector_id} -> {clean_name}")
                
            except InspectorMapping.DoesNotExist:
                # Create new mapping
                mapping = InspectorMapping.objects.create(
                    inspector_id=inspector_id,
                    inspector_name=clean_name,
                    is_active=True
                )
                created_count += 1
                print(f"✅ Created: ID {inspector_id} -> {clean_name}")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error processing ID {inspector_id} ({first_name} {last_name}): {e}")
    
    print("\n" + "=" * 80)
    print("📈 INSPECTOR MAPPING SUMMARY")
    print("=" * 80)
    print(f"✅ Created: {created_count} new mappings")
    print(f"🔄 Updated: {updated_count} existing mappings")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total Processed: {len(inspector_data)}")
    
    # Show all mappings
    print(f"\n🔗 ALL INSPECTOR MAPPINGS:")
    print("-" * 60)
    
    all_mappings = InspectorMapping.objects.all().order_by('inspector_id')
    for mapping in all_mappings:
        status = "🟢 Active" if mapping.is_active else "🔴 Inactive"
        print(f"ID {mapping.inspector_id:3d}: {mapping.inspector_name} ({status})")

if __name__ == "__main__":
    try:
        create_inspector_mappings()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)
