"""
The Dark Room - Terminal Access
A 3D hacking exploration game built with Ursina Engine.

NOTE: This project is no longer maintained.
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import time as systime

app = Ursina()

# Window settings
window.title = 'The Dark Room - Terminal Access'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = False

# Atmosphere
Sky(color=color.black)
scene.fog_color = color.black
scene.fog_density = (20, 150)

# --- CITY OUTSIDE ---
ground = Entity(model='plane', scale=1000, color=color.rgb(0.08, 0.15, 0.08), collider='box')

player_money = 0
money_text = Text(text="$0", position=(0.75, 0.45), scale=2, color=color.lime, origin=(0.5, 0.5))

flying_cars = []

# Create a parent entity to combine buildings for better performance
city_parent = Entity()

# --- HOST BUILDING (The building our room is in) ---
host_color = color.rgb(0.12, 0.15, 0.18)
# Behind the room (z from -38 to -8)
Entity(parent=city_parent, model='cube', color=host_color, scale=(38, 140, 30), position=(-11, 70, -23))
# Above the room (y from 130 to 140, z from -8 to 8)
Entity(parent=city_parent, model='cube', color=host_color, scale=(38, 10, 16), position=(-11, 135, 0))
# Below the room (y from 0 to 120, z from -8 to 8)
Entity(parent=city_parent, model='cube', color=host_color, scale=(38, 120, 16), position=(-11, 60, 0))
# Left of the room (x from -30 to -8, y from 120 to 130)
Entity(parent=city_parent, model='cube', color=host_color, scale=(22, 10, 16), position=(-19, 125, 0))
# (Host building neon removed)

# --- TERRAIN HILLS ---
for _ in range(60):
    hx, hz = random.uniform(-400, 400), random.uniform(-400, 400)
    hr = random.uniform(50, 150)
    hh = random.uniform(5, 25)
    
    # Keep the central area (host building / elevator) flat
    if abs(hx) < 100 and abs(hz) < 100: continue
    # Keep dealership area flat
    if abs(hx + 150) < 80 and abs(hz - 180) < 80: continue
    
    # Use Mesh collider for perfect smooth hill walking
    hill = Entity(model='sphere', scale=(hr, hh, hr), position=(hx, -hh/2 + 0.5, hz), color=color.rgb(0.08, 0.16, 0.08), collider='mesh')

cafe_networks = []
baristas = []

class Barista(Entity):
    def __init__(self, gx, gz, ssid):
        super().__init__(model='cube', color=color.green, scale=(1.2, 2.0, 1.2), position=(gx+2, 1.5, gz+6), collider='box')
        self.ssid = ssid
        self.head = Entity(parent=self, model='sphere', color=color.white, scale=0.8, position=(0, 0.8, 0))
        self.speech_text = Text(parent=self, text="Welcome!\nFresh coffee!", scale=2.5, position=(0, 1.8, 0), billboard=True, color=color.yellow, origin=(0, 0))
        
        self.waypoints = [
            Vec3(gx+2, 1.5, gz+6),   # 0. Behind counter
            Vec3(gx-5, 1.5, gz+6),   # 1. Left of counter
            Vec3(gx-5, 1.5, gz-6),   # 2. Near front wall inside
            Vec3(gx-1.5, 1.5, gz-10),# 3. Through the door opening
            Vec3(gx, 1.5, gz-15),    # 4. Center table (outside)
            Vec3(gx-5, 1.5, gz-15),  # 5. Left table
            Vec3(gx+5, 1.5, gz-15),  # 6. Right table
            Vec3(gx-1.5, 1.5, gz-10),# 7. Back through door
            Vec3(gx-5, 1.5, gz-6),   # 8. Near front wall inside
            Vec3(gx-5, 1.5, gz+6),   # 9. Left of counter
        ]
        self.wait_times = [8.0, 0.0, 0.0, 0.0, 3.0, 4.0, 4.0, 0.0, 0.0, 0.0]
        self.current_wp = 0
        self.wait_timer = self.wait_times[0]
        self.speed = 3.0
        
    def update(self):
        # Pause while cops are investigating
        global wanted_level
        if wanted_level > 0.1:
            self.look_at(player.position)
            self.rotation = Vec3(0, self.rotation_y, 0)
            return

        if self.wait_timer > 0:
            self.wait_timer -= time.dt
            if self.wait_timer <= 0:
                self.current_wp = (self.current_wp + 1) % len(self.waypoints)
            return
            
        target = self.waypoints[self.current_wp]
        direction = target - self.position
        direction.y = 0
        dist = direction.length()
        
        if dist < 0.2:
            self.position = target
            self.wait_timer = self.wait_times[self.current_wp]
        else:
            direction = direction.normalized()
            self.position += direction * self.speed * time.dt
            self.look_at(self.position + direction)
            self.rotation = Vec3(0, self.rotation_y, 0)

# Select EXACTLY 12 Cafe spots spread out everywhere
cafe_spots = []
valid_coords = list(range(-360, 400, 80))
while len(cafe_spots) < 12:
    cx = random.choice(valid_coords)
    cz = random.choice(valid_coords)
    if abs(cx) < 100 and abs(cz) < 100: continue
    if abs(cx + 150) < 80 and abs(cz - 180) < 80: continue
    if (cx, cz) not in cafe_spots:
        cafe_spots.append((cx, cz))

# Structured Block Building Generation
for gx in range(-360, 400, 80):
    for gz in range(-360, 400, 80):
        if (gx, gz) in cafe_spots:
            # Hollow Cafe Structure
            hc = color.rgb(0.9, 0.8, 0.7)
            # Floor
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(20, 0.5, 20), position=(gx, 0, gz), color=color.rgb(0.3, 0.2, 0.2))
            # Left Wall
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(1, 12, 20), position=(gx-9.5, 0, gz), color=hc)
            # Right Wall
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(1, 12, 20), position=(gx+9.5, 0, gz), color=hc)
            # Back Wall
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(18, 12, 1), position=(gx, 0, gz+9.5), color=hc)
            
            # Front Header
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(18, 4, 1), position=(gx, 8, gz-9.5), color=hc)
            # Front Wall Left (door opening)
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(6, 8, 1), position=(gx-6, 0, gz-9.5), color=hc)
            # Front Wall Right (window opening)
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(9, 3, 1), position=(gx+4.5, 0, gz-9.5), color=hc)
            
            # Open Door Model (Fixed at 45 degree angle so they can walk in)
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(3, 8, 0.2), position=(gx-2, 0, gz-10), rotation_y=-45, color=color.rgb(0.4, 0.2, 0.1))
            # Window Glass
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(9, 5, 0.2), position=(gx+4.5, 3, gz-9.5), color=color.rgba(200, 220, 255, 150))
            
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(22, 1.5, 22), position=(gx, 12, gz), color=color.rgb(0.2, 0.2, 0.2)) # Roof
            Entity(parent=city_parent, model='cube', scale=(18, 0.5, 7), rotation_x=15, position=(gx, 8, gz-12), color=random.choice([color.red, color.green, color.orange])) # Awning

            # Interior Cafe Counter
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(10, 1.5, 2), position=(gx+2, 0.5, gz+3), color=color.rgb(0.2, 0.1, 0.05))
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(10.5, 0.2, 2.5), position=(gx+2, 2.0, gz+3), color=color.light_gray)

            # Cafe network setup
            ssid = f"Cafe_Net_{random.randint(1000, 9999)}"
            password = ''.join(random.choices("ABCDEF123456789", k=8))
            cafe_networks.append({"ssid": ssid, "password": password, "pos": Vec3(gx, 0, gz)})

            # NPC Barista
            barista = Barista(gx, gz, ssid)
            baristas.append(barista)

            # Seating remains the same outside
            for sx in [-5, 0, 5]:
                Entity(parent=city_parent, model='sphere', scale=(3, 0.2, 3), position=(gx+sx, 1.5, gz-15), color=color.white) # Tabletop
                Entity(parent=city_parent, model='cube', scale=(0.3, 1.5, 0.3), position=(gx+sx, 0.75, gz-15), color=color.gray) # Table leg
                Entity(parent=city_parent, model='cube', scale=(1.2, 1, 1.2), position=(gx+sx-2, 0.5, gz-15), color=color.rgb(0.3, 0.2, 0.1)) # Chair L
                Entity(parent=city_parent, model='cube', scale=(1.2, 1, 1.2), position=(gx+sx+2, 0.5, gz-15), color=color.rgb(0.3, 0.2, 0.1)) # Chair R
            
            # Billboard Sign
            Text(parent=scene, text='CAFE', scale=25, position=(gx-3, 13, gz-11), color=color.yellow, billboard=True)
            continue

        if random.random() < 0.15: # 15% chance to have an empty block (park, plaza, etc.)
            # Generate a few low-poly trees for the park
            for _ in range(random.randint(3, 8)):
                tx, tz = gx + random.uniform(-20, 20), gz + random.uniform(-20, 20)
                th = random.uniform(3, 8)
                trunk = Entity(parent=city_parent, model='cube', scale=(1.0, th, 1.0), position=(tx, 0, tz), color=color.rgb(0.35, 0.2, 0.1), origin_y=-0.5)
                Entity(parent=trunk, model='sphere', scale=(3.5, 1.2, 3.5), position=(0, 1.0, 0), color=color.rgb(0.1, 0.5, 0.1))
            continue

        x, z = gx, gz
        # Modest width, drastic reduction in height to escape "pillar" look
        w, d = random.uniform(25, 45), random.uniform(25, 45)
        h = random.uniform(15, 60) 
        
        # Don't spawn buildings inside the starting room or host building area
        if abs(x) < 70 and abs(z) < 70: continue
        # Keep clear of the dealership
        if abs(x + 150) < 60 and abs(z - 180) < 60: continue
            
        # Natural building colors (bricks, wood, plaster, olive)
        color_choices = [color.rgb(0.6, 0.3, 0.2), color.rgb(0.4, 0.3, 0.2), color.rgb(0.7, 0.7, 0.6), color.rgb(0.3, 0.4, 0.3)]
        base_c = random.choice(color_choices)
        shade = random.uniform(0.7, 1.1)
        building_color = color.rgb(base_c.r * shade, base_c.g * shade, base_c.b * shade)
        roof_color = color.rgb(0.18, 0.18, 0.18)
        
        # Tier 1 (Main structure)
        Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(w, h, d), position=(x, 0, z), color=building_color)
        Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(w+3, 2, d+3), position=(x, h, z), color=roof_color) # Overhang Roof
        
        top_y = h + 2

        # Side extensions for L-shape variations
        if random.random() > 0.5:
            ew, ed = random.uniform(15, 25), random.uniform(15, 25)
            eh = random.uniform(10, h * 0.7)
            # Offset to corner
            ex = x + random.choice([w/2, -w/2])
            ez = z + random.choice([d/2, -d/2])
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(ew, eh, ed), position=(ex, 0, ez), color=building_color)
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(ew+2, 1.5, ed+2), position=(ex, eh, ez), color=roof_color)

        # Multi-tier design (if tall enough, add another tier on top)
        if h > 30 and random.random() > 0.3:
            h2 = random.uniform(10, h * 0.5)
            w2, d2 = w * 0.7, d * 0.7
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(w2, h2, d2), position=(x, top_y, z), color=building_color)
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(w2+2, 1.5, d2+2), position=(x, top_y+h2, z), color=roof_color)
            top_y += h2 + 1.5
        
        # Add little chimneys on top to break up flat tops
        for _ in range(random.randint(1, 4)):
            cx, cz = x + random.uniform(-w/4, w/4), z + random.uniform(-d/4, d/4)
            Entity(parent=city_parent, model='cube', origin_y=-0.5, scale=(1.5, random.uniform(2, 6), 1.5), position=(cx, top_y, cz), color=color.rgb(0.4, 0.2, 0.2))

# Combine building meshes into one single mesh drastically improving FPS
city_parent.combine()


# --- STARTING ROOM ---
room_parent = Entity(position=(0, 120, 0))

room_size = 15
room_height = 10
Wall = Entity(parent=room_parent, model='cube', color=color.black, collider='box')

duplicate(Wall, scale=(room_size, room_height, 1), position=(0, room_height/2, -room_size/2)) # Back wall
duplicate(Wall, scale=(1, room_height, room_size), position=(-room_size/2, room_height/2, 0)) # Left wall

# Right wall with a window
duplicate(Wall, scale=(1, 3, room_size), position=(room_size/2, 1.5, 0)) # Bottom piece
duplicate(Wall, scale=(1, 3, room_size), position=(room_size/2, 8.5, 0)) # Top piece
duplicate(Wall, scale=(1, 4, 4.5), position=(room_size/2, 5, -5.25)) # Left piece
duplicate(Wall, scale=(1, 4, 4.5), position=(room_size/2, 5, 5.25)) # Right piece
# Window glass
Entity(parent=room_parent, model='cube', scale=(0.5, 4, 6), position=(room_size/2, 5, 0), color=color.rgba(150, 200, 255, 120), collider='box')

duplicate(Wall, scale=(room_size, 1, room_size), position=(0, room_height, 0)) # Roof
duplicate(Wall, scale=(room_size, 0.1, room_size), position=(0, 0, 0), color=color.rgb(0.1, 0.1, 0.1)) # Floor

# Front wall
door_w, door_h = 3, 5
duplicate(Wall, scale=((room_size-door_w)/2, room_height, 1), position=(-(room_size+door_w)/4, room_height/2, room_size/2))
duplicate(Wall, scale=((room_size-door_w)/2, room_height, 1), position=((room_size+door_w)/4, room_height/2, room_size/2))
duplicate(Wall, scale=(door_w, room_height-door_h, 1), position=(0, (room_height+door_h)/2, room_size/2))

# Balcony so door doesn't open in the air
Entity(parent=room_parent, model='cube', scale=(room_size, 0.2, 6), position=(0, 0, room_size/2 + 3), color=color.dark_gray, collider='box')
# Balcony railings (solid on front/left, right side open for elevator)
Entity(parent=room_parent, model='cube', scale=(15, 1.2, 0.2), position=(0, 0.6, 13.5), color=color.gray, collider='box') # Front
Entity(parent=room_parent, model='cube', scale=(0.2, 1.2, 6), position=(-7.5, 0.6, 10.5), color=color.gray, collider='box') # Left
# Right railing removed!

# --- ELEVATOR ---
elevator_x = 8.8
elevator_z = 10.5

# Elevator rails to make a "place" for it
Entity(parent=city_parent, model='cube', scale=(0.2, 130, 0.2), position=(elevator_x - 1.2, 65, elevator_z - 1.2), color=color.dark_gray)
Entity(parent=city_parent, model='cube', scale=(0.2, 130, 0.2), position=(elevator_x + 1.2, 65, elevator_z + 1.2), color=color.dark_gray)
# Ground landing pad
Entity(parent=city_parent, model='cube', scale=(4, 0.2, 4), position=(elevator_x, 0, elevator_z), color=color.gray)

elevator = Entity(model='cube', color=color.rgb(0.2, 0.2, 0.2), scale=(2.5, 1.0, 2.5), position=(elevator_x, 120.0, elevator_z), origin_y=0.5, collider='box')
# Left side is OPEN to enter from balcony
Entity(parent=elevator, model='cube', scale=(0.1, 8, 2.5), position=(1.2, 4, 0), color=color.rgba(150, 200, 255, 80), collider='box') # Right glass
Entity(parent=elevator, model='cube', scale=(2.5, 8, 0.1), position=(0, 4, 1.2), color=color.rgba(150, 200, 255, 80), collider='box') # Front glass
Entity(parent=elevator, model='cube', scale=(2.5, 8, 0.1), position=(0, 4, -1.2), color=color.rgba(150, 200, 255, 80), collider='box') # Back glass
Entity(parent=elevator, model='cube', scale=(2.5, 0.2, 2.5), position=(0, 8, 0), color=color.gray, collider='box') # Roof

# In-elevator buttons Panel (on the right wall)
ev_panel = Entity(parent=elevator, model='cube', scale=(0.2, 1.5, 1.5), position=(1.15, 1.5, 0), color=color.gray, collider='box')
btn_up = Entity(parent=ev_panel, model='cube', scale=(0.5, 0.4, 0.8), position=(-0.5, 0.25, 0), color=color.green, collider='box')
btn_down = Entity(parent=ev_panel, model='cube', scale=(0.5, 0.4, 0.8), position=(-0.5, -0.25, 0), color=color.red, collider='box')
Text(parent=btn_up, text='UP', scale=5, position=(-0.6, 0.2, 0), rotation_y=-90, color=color.white)
Text(parent=btn_down, text='DOWN', scale=5, position=(-0.6, 0.2, 0), rotation_y=-90, color=color.white)

# Call Button Top (on Balcony, right next to elevator entrance)
call_top_btn = Entity(parent=room_parent, model='cube', scale=(0.5, 1.5, 0.5), position=(7.0, 1.5, 8.5), color=color.yellow, collider='box')
Text(parent=call_top_btn, text='CALL', scale=5, position=(-0.6, 0.3, 0), rotation_y=-90, color=color.black)

# Call Button Bottom (Ground floor, gigantic pillar)
call_bot_btn = Entity(parent=city_parent, model='cube', scale=(1.5, 3.0, 1.5), position=(6.0, 1.5, 10.5), color=color.yellow, collider='box')
Text(parent=call_bot_btn, text='CALL', scale=3, position=(-0.6, 0.3, 0), rotation_y=-90, color=color.black)
Text(parent=call_bot_btn, text='CALL', scale=3, position=(0.6, 0.3, 0), rotation_y=90, color=color.black)

# --- BICYCLE ---
bicycle = Entity(position=(12, 0.1, 15), rotation_y=30, scale=1.8)
bike_col = 'box'

# Wheels (Using flattened spheres since cylinder is unavailable)
Entity(parent=bicycle, model='sphere', scale=(0.6, 0.05, 0.6), rotation_x=90, color=color.dark_gray, position=(-0.6, 0.3, 0), collider=bike_col)
Entity(parent=bicycle, model='sphere', scale=(0.55, 0.06, 0.55), rotation_x=90, color=color.black, position=(-0.6, 0.3, 0)) # Tire tread
Entity(parent=bicycle, model='sphere', scale=(0.6, 0.05, 0.6), rotation_x=90, color=color.dark_gray, position=(0.6, 0.3, 0), collider=bike_col)
Entity(parent=bicycle, model='sphere', scale=(0.55, 0.06, 0.55), rotation_x=90, color=color.black, position=(0.6, 0.3, 0)) # Tire tread

# Frame (Proper geometrical triangle frame)
Entity(parent=bicycle, model='cube', scale=(0.8, 0.03, 0.03), color=color.red, position=(0.1, 0.65, 0), collider=bike_col)       # Top tube
Entity(parent=bicycle, model='cube', scale=(0.8, 0.03, 0.03), rotation_z=-35, color=color.red, position=(0.1, 0.45, 0), collider=bike_col) # Down tube
Entity(parent=bicycle, model='cube', scale=(0.04, 0.65, 0.04), rotation_z=-15, color=color.red, position=(-0.25, 0.45, 0), collider=bike_col)# Seat tube
Entity(parent=bicycle, model='cube', scale=(0.45, 0.03, 0.03), color=color.red, position=(-0.4, 0.3, 0), collider=bike_col)      # Chain stay
Entity(parent=bicycle, model='cube', scale=(0.03, 0.5, 0.03), rotation_z=45, color=color.red, position=(-0.45, 0.55, 0), collider=bike_col) # Seat stay

# Front Fork
Entity(parent=bicycle, model='cube', scale=(0.04, 0.5, 0.04), rotation_z=15, color=color.rgb(0.8, 0.8, 0.8), position=(0.52, 0.5, 0), collider=bike_col)

# Handlebars & Stem
Entity(parent=bicycle, model='cube', scale=(0.03, 0.2, 0.03), color=color.dark_gray, position=(0.45, 0.75, 0), collider=bike_col)
Entity(parent=bicycle, model='cube', scale=(0.03, 0.03, 0.6), color=color.black, position=(0.45, 0.85, 0), collider=bike_col)

# Seat
Entity(parent=bicycle, model='cube', scale=(0.25, 0.06, 0.12), color=color.black, position=(-0.35, 0.8, 0), collider=bike_col)

# Crank & Pedals
Entity(parent=bicycle, model='sphere', scale=(0.12, 0.1, 0.12), rotation_x=90, color=color.dark_gray, position=(-0.15, 0.3, 0))
Entity(parent=bicycle, model='cube', scale=(0.03, 0.35, 0.03), color=color.rgb(0.8, 0.8, 0.8), position=(-0.15, 0.3, 0))
Entity(parent=bicycle, model='cube', scale=(0.08, 0.03, 0.1), color=color.black, position=(-0.15, 0.48, 0.05)) # Pedal 1
Entity(parent=bicycle, model='cube', scale=(0.08, 0.03, 0.1), color=color.black, position=(-0.15, 0.12, -0.05)) # Pedal 2

# --- CAR DEALER BUILDING ---
dealership_pos = Vec3(-150, 0, 180)
dealer_parent = Entity(position=dealership_pos)

# Dealership Structure
Entity(parent=dealer_parent, model='cube', scale=(26, 0.2, 18), position=(0, 0.1, 0), color=color.dark_gray, collider='box') # Floor
Entity(parent=dealer_parent, model='cube', scale=(24, 10, 0.5), position=(0, 5, 7.5), color=color.gray, collider='box') # Back Wall
Entity(parent=dealer_parent, model='cube', scale=(0.5, 10, 15), position=(-12, 5, 0), color=color.gray, collider='box') # Left Wall
Entity(parent=dealer_parent, model='cube', scale=(0.5, 10, 15), position=(12, 5, 0), color=color.gray, collider='box') # Right Wall
Entity(parent=dealer_parent, model='cube', scale=(26, 0.5, 20), position=(0, 10, -1), color=color.rgb(0.2,0.2,0.2), collider='box') # Roof
Entity(parent=dealer_parent, model='cube', scale=(24, 0.2, 4), position=(0, 8, -9.5), color=color.black) # Awning

# Showroom Glass Front (Split into sections to make room for door)
Entity(parent=dealer_parent, model='cube', scale=(8, 10, 0.1), position=(-8, 5, -7.5), color=color.rgba(180, 220, 255, 80), collider='box') # Left
Entity(parent=dealer_parent, model='cube', scale=(8, 10, 0.1), position=(8, 5, -7.5), color=color.rgba(180, 220, 255, 80), collider='box') # Right
Entity(parent=dealer_parent, model='cube', scale=(8, 3, 0.1), position=(0, 8.5, -7.5), color=color.rgba(180, 220, 255, 80), collider='box') # Top Header

# Interactive Dealership Door (With clear frames and a handlebar)
dealer_door_pivot = Entity(parent=dealer_parent, position=(-4, 0, -7.5))
dealer_door = Entity(parent=dealer_door_pivot, model='cube', scale=(8, 7, 0.1), position=(4, 3.5, 0), color=color.rgba(180, 220, 255, 50), collider='box')
dealer_door_handle = Entity(parent=dealer_door, model='cube', scale=(0.02, 0.2, 3.0), position=(0.4, 0, 0), color=color.light_gray)
dealer_door_frame_top = Entity(parent=dealer_door, model='cube', scale=(1.01, 0.05, 1.2), position=(0, 0.5, 0), color=color.black)
dealer_door_frame_left = Entity(parent=dealer_door, model='cube', scale=(0.02, 1.01, 1.2), position=(-0.5, 0, 0), color=color.black)
dealer_door_frame_right = Entity(parent=dealer_door, model='cube', scale=(0.02, 1.01, 1.2), position=(0.5, 0, 0), color=color.black)

Entity(parent=dealer_parent, model='cube', scale=(8, 0.5, 0.3), position=(-8, 0.25, -7.5), color=color.black) # Bottom Frame Left
Entity(parent=dealer_parent, model='cube', scale=(8, 0.5, 0.3), position=(8, 0.25, -7.5), color=color.black) # Bottom Frame Right
Entity(parent=dealer_parent, model='cube', scale=(24, 0.5, 0.3), position=(0, 9.75, -7.5), color=color.black) # Top Frame
for x in [-12, -4, 4, 12]: 
    Entity(parent=dealer_parent, model='cube', scale=(0.4, 10, 0.3), position=(x, 5, -7.5), color=color.black) # Pillars

# Desk
desk = Entity(parent=dealer_parent, model='cube', scale=(6, 1.2, 2.5), position=(0, 0.6, 5), color=color.rgb(50, 40, 30), collider='box')
Entity(parent=desk, model='cube', scale=(0.05, 1.2, 2.3), position=(-0.48, -0.5, 0), color=color.black) # Leg L
Entity(parent=desk, model='cube', scale=(0.05, 1.2, 2.3), position=(0.48, -0.5, 0), color=color.black) # Leg R

# NPC (Salesman)
salesman = Entity(parent=dealer_parent, model='cube', scale=(1.2, 2.0, 1.2), position=(0, 1.0, 6.7), color=color.orange, collider='box')
Entity(parent=salesman, model='sphere', color=color.white, scale=0.8, position=(0, 0.8, 0))
Text(parent=salesman, text='Hello!\nWant to buy a car?', scale=2.5, position=(0, 1.5, 0), billboard=True, color=color.yellow, origin=(0, 0))
salesman.rotation_y = 180

# Signage
Entity(parent=dealer_parent, model='cube', scale=(10, 3, 0.5), position=(0, 11.5, -7.3), color=color.black)
Entity(parent=dealer_parent, model='cube', scale=(9.5, 2.5, 0.6), position=(0, 11.5, -7.3), color=color.red)
Text(parent=dealer_parent, text="CITY MOTORS", scale=20, position=(-3.2, 11.8, -7.7), color=color.white)

# Interior Lighting
for x in [-8, 0, 8]:
    Entity(parent=dealer_parent, model='cube', scale=(0.4, 0.1, 12), position=(x, 9.7, 0), color=color.white, unlit=True)

def make_car(parent_ent, pos, rot_y, car_color):
    car = Entity(parent=parent_ent, position=pos, rotation_y=rot_y)
    Entity(parent=car, model='cube', scale=(2.2, 0.6, 5), position=(0, 0.6, 0), color=car_color, collider='box') # Chassis
    Entity(parent=car, model='cube', scale=(1.8, 0.7, 2.5), position=(0, 1.25, -0.2), color=color.black) # Cabin
    for wx in [-1.2, 1.2]: # Wheels
        for wz in [-1.8, 1.8]:
            Entity(parent=car, model='sphere', scale=(0.6, 0.6, 0.6), position=(wx, 0.3, wz), color=color.dark_gray)
    for wx in [-0.8, 0.8]: # Headlights
        Entity(parent=car, model='cube', scale=(0.4, 0.2, 0.1), position=(wx, 0.7, 2.5), color=color.yellow, unlit=True)
    for wx in [-0.8, 0.8]: # Taillights
        Entity(parent=car, model='cube', scale=(0.4, 0.2, 0.1), position=(wx, 0.7, -2.5), color=color.red, unlit=True)
    Entity(parent=car, model='cube', scale=(1.2, 0.3, 0.11), position=(0, 0.5, 2.5), color=color.black) # Grill

# Cars on display
Entity(parent=dealer_parent, model='cube', scale=(8, 0.2, 9), position=(-6, 0.2, 0), color=color.white) # Pedestal 1
make_car(dealer_parent, Vec3(-6, 0.3, 0), 25, color.red)

Entity(parent=dealer_parent, model='cube', scale=(8, 0.2, 9), position=(6, 0.2, 0), color=color.white) # Pedestal 2
make_car(dealer_parent, Vec3(6, 0.3, 0), -15, color.cyan)

# Outdoor display
make_car(dealer_parent, Vec3(-10, 0, -15), 45, color.magenta)
# --- GPS NAVIGATION PATH ---
gps_path = Entity(enabled=False)

def set_nav_target(target_world_pos):
    for c in gps_path.children:
        destroy(c)
    # direct line from building base to target
    start = Vec3(4, 0.2, 8)
    end = Vec3(target_world_pos.x, 0.2, target_world_pos.z)
    steps = max(2, int(distance(start, end) / 1.5))
    for j in range(steps):
        t = j / steps
        pos = lerp(start, end, t)
        Entity(parent=gps_path, model='cube', scale=0.4, position=pos, color=color.cyan)

set_nav_target(Vec3(-150, 0, 180)) # Default to dealership

# Hide original wall template
Wall.enabled = False

# --- INTERACTABLES ---
door_pivot = Entity(parent=room_parent, position=(door_w/2, 0, room_size/2))
door = Entity(parent=door_pivot, model='cube', scale=(door_w, door_h, 0.2), position=(-door_w/2, door_h/2, 0), color=color.rgb(40, 30, 10), collider='box')
door_knob = Entity(parent=door, model='sphere', scale=(0.15, 0.15, 0.5), position=(-door_w + 0.5, 0, 0), color=color.gold)

table = Entity(parent=room_parent, model='cube', scale=(4, 0.2, 2.5), position=(0, 1.2, -4), color=color.rgb(50, 40, 30), collider='box')
leg_p = {'model':'cube', 'scale':(0.15, 1.2, 0.15), 'color':color.rgb(30, 20, 10), 'parent':table, 'origin_y':0.5}
Entity(position=(0.4, -0.5, 0.4), **leg_p); Entity(position=(-0.4, -0.5, 0.4), **leg_p)
Entity(position=(0.4, -0.5, -0.4), **leg_p); Entity(position=(-0.4, -0.5, -0.4), **leg_p)

laptop = Entity(parent=room_parent, position=(0, 1.3, -4))
laptop_base = Entity(parent=laptop, model='cube', scale=(1.2, 0.06, 0.8), position=(0, 0, 0), color=color.black, collider='box')
laptop_screen_pivot = Entity(parent=laptop, position=(0, 0, 0.4))
laptop_screen = Entity(parent=laptop_screen_pivot, model='cube', scale=(1.2, 0.8, 0.06), position=(0, 0.4, 0), rotation_x=-25, color=color.black)
screen_glow = Entity(parent=laptop_screen, model='plane', scale=(0.9, 0.7, 1), position=(0, 0, -0.04), rotation_x=-90, color=color.green)
laptop_light = PointLight(parent=laptop, position=(0, 1, 0), color=color.green, shadows=True)

# --- INTERACTIVE TERMINAL ---
class TerminalUI(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, model='quad', scale=(0.8, 0.6), color=color.black66, enabled=False, z=-1)
        self.header = Entity(parent=self, model='quad', scale=(1, 0.12), position=(0, 0.44, -0.1), color=color.black)
        self.header_text = Text(text=" SYSTEM TERMINAL v1.0.4 - SHADOW_OS", parent=self.header, position=(-0.48, 0, -0.2), scale=1, color=color.green, origin=(-0.5, 0))
        
        self.log_text = Text(text='', parent=self, position=(-0.46, 0.32, -0.1), color=color.green, scale=1.2, line_height=1.1, origin=(-0.5, 0.5))
        self.lines = ["Connected to local backbone.", "Type 'help' for commands."]
        self.update_log()
        
        # Input handling
        self.input_label = Text(text=">", parent=self, position=(-0.46, -0.42, -0.1), color=color.green, scale=1.2)
        self.input_field = InputField(
            parent=self, 
            position=(0.02, -0.42, -0.1), 
            scale=(0.88, 0.05), 
            color=color.black90, 
            text_color=color.green,
            active=False
        )
        self.input_field.on_submit = self.process_command
        
    def update_log(self):
        if len(self.lines) > 50:
            self.lines = self.lines[-50:]
        self.log_text.text = '\n'.join(self.lines[-14:]) # Show a few more lines
        
    def add_line(self, text):
        self.lines.append(text)
        self.update_log()

    def process_command(self, *args):
        # We take *args to handle cases where Ursina passes the text or event
        cmd = self.input_field.text.strip().lower()
        if not cmd:
            self.input_field.active = True
            return
            
        self.add_line(f"> {cmd}")
        
        if cmd == 'help':
            self.add_line("Terminal Commands:")
            self.add_line("  help    - This manual")
            self.add_line("  nscan   - Scan networks")
            self.add_line("  npass   - Crack nearby network passwords")
            self.add_line("  nsubmit - Submit cracked network to client")
            self.add_line("  cls     - Clear screen")
            self.add_line("  exit    - Disconnect")
        elif cmd == 'nscan':
            self.add_line("Scanning airwaves...")
            found_any = False
            for net in cafe_networks:
                if distance(player.world_position, net['pos']) < 60:
                    status = "Fulfilled" if net['password'] == "hacked" else ("Cracked" if net.get('cracked') else "Secured")
                    self.add_line(f"Found: {net['ssid']} ({status})")
                    found_any = True
            if not found_any:
                self.add_line("Found: [neighbor_1, ghost_node, backbone_primary]")
        elif cmd == 'npass':
            nets_in_range = [net for net in cafe_networks if distance(player.world_position, net['pos']) < 60]
            if not nets_in_range:
                self.add_line("ERR: No active signals detected.")
            else:
                target_net = nets_in_range[0]
                if target_net['password'] == "hacked":
                    self.add_line("ERR: Network already exploited.")
                elif target_net.get('cracked'):
                    self.add_line(f"Network '{target_net['ssid']}' is already cracked.")
                    self.add_line(f"Password is: '{target_net['password']}'")
                else:
                    self.add_line(f"Target locked: {target_net['ssid']}")
                    self.add_line("Initiating handshake capture...")
                    invoke(self.add_line, "Bypassing MAC filters...", delay=2)
                    invoke(self.add_line, "Capturing 4-way authentication...", delay=4)
                    invoke(self.add_line, "Extracting PMKID hash...", delay=6)
                    invoke(self.add_line, "Running cryptographic dictionary...", delay=8)
                    def mark_cracked(t_net=target_net):
                        t_net['cracked'] = True
                        self.add_line(f"SUCCESS! Password is: '{t_net['password']}'")
                    invoke(mark_cracked, delay=10)
        elif cmd.startswith('nsubmit'):
            nets_in_range = [net for net in cafe_networks if distance(player.world_position, net['pos']) < 60]
            if not nets_in_range:
                self.add_line("ERR: No active signals detected.")
            else:
                target_net = nets_in_range[0]
                if target_net['password'] == "hacked":
                    self.add_line("ERR: Network contract already fulfilled.")
                elif not target_net.get('cracked'):
                    self.add_line("ERR: Network password unknown. Run 'npass' first.")
                else:
                    global player_money
                    player_money += 1500
                    money_text.text = f"${player_money}"
                    self.add_line("VERIFIED! Payment of $1500 routed anonymously.")
                    target_net['password'] = "hacked"
        elif cmd == 'cls':
            self.lines = ["Terminal cleared."]
        elif cmd == 'exit':
            toggle_terminal()
            return
        else:
            self.add_line(f"ERR: Command '{cmd}' not found.")
        
        self.input_field.text = ''
        self.input_field.active = True 
        self.update_log()

    def input(self, key):
        if self.enabled and key == 'enter':
            self.process_command()

terminal = TerminalUI()

# --- SMARTPHONE UI ---

class PhoneUI(Entity):
    def __init__(self):
        # Helper to safely make normalized colors 0.0-1.0
        def c(r,g,b): return color.rgba(r/255.0, g/255.0, b/255.0, 1.0)
        
        # Phone body - dark sleek bezel
        super().__init__(parent=camera.ui, model='quad', scale=(0.32, 0.62), position=(1.2, 0, -1), color=c(15, 15, 15), enabled=False)
        # Inner bezel highlight
        Entity(parent=self, model='quad', scale=(0.97, 0.98), position=(0, 0, -0.005), color=c(30, 30, 35))
        # Screen
        self.screen_bg = Entity(parent=self, model='quad', scale=(0.92, 0.92), position=(0, 0.01, -0.01), color=c(18, 18, 24))
        
        # Status Bar
        status_bar = Entity(parent=self.screen_bg, model='quad', scale=(1, 0.06), position=(0, 0.47, -0.02), color=c(10, 10, 16))
        self.time_text = Text(parent=status_bar, text='12:00', scale=2.5, position=(-0.42, 0, -0.01), origin=(-0.5, 0), color=color.white)
        # Signal bars
        for sb in range(4):
            h = 0.15 + sb * 0.15
            Entity(parent=status_bar, model='quad', scale=(0.02, h), position=(0.30 + sb*0.035, -0.15 + h/2, -0.01), color=c(80, 220, 120))
        # Battery
        Entity(parent=status_bar, model='quad', scale=(0.08, 0.35), position=(0.46, 0, -0.01), color=c(40, 40, 50))
        Entity(parent=status_bar, model='quad', scale=(0.065, 0.25), position=(0.46, 0, -0.02), color=c(80, 220, 120))
        Entity(parent=status_bar, model='quad', scale=(0.015, 0.12), position=(0.498, 0, -0.01), color=c(40, 40, 50))

        # App Grid
        app_data = [
            ('MAPS',  c(40, 100, 220), c(80, 140, 255), self.open_maps),
            ('JOBS',  c(220, 120, 30),  c(255, 160, 70), self.open_requests),
            ('CHAT',  c(50, 180, 80),   c(90, 220, 120), None),
            ('CAM',   c(180, 50, 180),  c(220, 90, 220), None),
            ('MUSIC', c(220, 50, 80),   c(255, 90, 120), None),
            ('STORE', c(50, 180, 220),  c(90, 220, 255), None),
        ]
        self.apps = []
        for i, (name, col, h_col, action) in enumerate(app_data):
            x = (i % 3 - 1) * 0.3
            y = 0.22 - (i // 3) * 0.32
            btn = Button(parent=self.screen_bg, model='quad', scale=(0.22, 0.22), position=(x, y, -0.02))
            btn.color = col
            btn.highlight_color = h_col
            Text(parent=self.screen_bg, text=name, scale=1.5, position=(x, y - 0.14, -0.02), origin=(0,0), color=c(180, 180, 190))
            if action:
                btn.on_click = action
            self.apps.append(btn)
            
        # Home Bar
        Entity(parent=self, model='quad', scale=(0.25, 0.008), position=(0, -0.44, -0.02), color=c(120, 120, 130))
        self.home_btn = Button(parent=self, model='quad', scale=(0.25, 0.04), position=(0, -0.44, -0.03), color=color.clear)
        self.home_btn.highlight_color = color.clear
        self.home_btn.on_click = self.go_home

        # Maps Screen
        self.map_ui = Entity(parent=self.screen_bg, model='quad', scale=(0.98, 0.88), position=(0, -0.02, -0.03), color=c(14, 14, 20), enabled=False)
        Entity(parent=self.map_ui, model='quad', scale=(1, 0.08), position=(0, 0.46, -0.01), color=c(40, 100, 220))
        Text(parent=self.map_ui, text='CITY MAPS', scale=2.2, position=(0, 0.46, -0.02), origin=(0,0), color=color.white)
        Entity(parent=self.map_ui, model='quad', scale=(0.85, 0.35), position=(0, 0.12, -0.01), color=c(28, 28, 38))
        Text(parent=self.map_ui, text='CAR DEALERSHIP', scale=2, position=(0, 0.22, -0.02), origin=(0,0), color=c(80, 200, 255))
        Text(parent=self.map_ui, text='Follow the glowing\ncyan path to\nthe dealership!', scale=1.5, position=(0, 0.06, -0.02), origin=(0,0), color=c(160, 160, 170))
        self.nav_btn = Button(parent=self.map_ui, text='NAVIGATE', scale=(0.7, 0.12), position=(0, -0.2, -0.01))
        self.nav_btn.color = c(40, 100, 220)
        self.nav_btn.highlight_color = c(60, 130, 255)
        self.nav_btn.text_entity.color = color.white
        self.nav_btn.on_click = self.toggle_nav

        # Requests Screen
        self.req_ui = Entity(parent=self.screen_bg, model='quad', scale=(0.98, 0.88), position=(0, -0.02, -0.03), color=c(14, 14, 20), enabled=False)
        Entity(parent=self.req_ui, model='quad', scale=(1, 0.08), position=(0, 0.46, -0.01), color=c(220, 120, 30))
        Text(parent=self.req_ui, text='ACTIVE JOBS', scale=2.2, position=(0, 0.46, -0.02), origin=(0,0), color=color.white)
        self.req_buttons = []
        self.req_built = False

        self.is_open = False

    def open_maps(self):
        self.go_home()
        self.map_ui.enabled = True
        set_nav_target(Vec3(-150, 0, 180))
        gps_path.enabled = True
        self.nav_btn.color = color.rgba(220/255, 50/255, 50/255, 1)
        self.nav_btn.text = 'STOP NAV'
        self.nav_btn.text_entity.color = color.white

    def open_requests(self):
        self.go_home()
        self.req_ui.enabled = True
        if not self.req_built and len(cafe_networks) > 0:
            self.req_built = True
            count = min(3, len(cafe_networks))
            job_cafes = random.sample(cafe_networks, count)
            for j, t_cafe in enumerate(job_cafes):
                def make_click_func(tc):
                    def do_nav():
                        set_nav_target(tc['pos'])
                        gps_path.enabled = True
                        self.go_home()
                    return do_nav
                
                def c(r,g,b): return color.rgba(r/255.0, g/255.0, b/255.0, 1.0)
                Entity(parent=self.req_ui, model='quad', scale=(0.85, 0.18), position=(0, 0.22 - j*0.25, -0.01), color=c(28, 28, 38))
                jb = Button(parent=self.req_ui, text=f">> {t_cafe['ssid']}", scale=(0.8, 0.12), position=(0, 0.22 - j*0.25, -0.02))
                jb.color = c(30, 30, 42)
                jb.highlight_color = c(180, 50, 50)
                jb.text_entity.color = c(80, 255, 120)
                jb.on_click = make_click_func(t_cafe)
                self.req_buttons.append(jb)

    def go_home(self):
        self.map_ui.enabled = False
        self.req_ui.enabled = False

    def toggle_nav(self):
        gps_path.enabled = not gps_path.enabled
        def c(r,g,b): return color.rgba(r/255.0, g/255.0, b/255.0, 1.0)
        if gps_path.enabled:
            self.nav_btn.color = c(220, 50, 50)
            self.nav_btn.text = 'STOP NAV'
        else:
            self.nav_btn.color = c(40, 100, 220)
            self.nav_btn.text = 'NAVIGATE'
        self.nav_btn.text_entity.color = color.white

    def update(self):
        self.time_text.text = systime.strftime("%H:%M")

    def toggle(self):
        if not self.is_open:
            self.enabled = True
            self.animate_position((0.65, 0, -1), duration=0.3, curve=curve.out_expo)
            self.is_open = True
            mouse.locked = False
            mouse.visible = True
            player.enabled = False
        else:
            self.animate_position((1.2, 0, -1), duration=0.3, curve=curve.in_expo)
            invoke(setattr, self, 'enabled', False, delay=0.3)
            self.is_open = False
            if not terminal.enabled:
                mouse.locked = True
                mouse.visible = False
                player.enabled = True

phone = PhoneUI()

def toggle_terminal():
    terminal.enabled = not terminal.enabled
    player.enabled = not terminal.enabled
    mouse.visible = terminal.enabled
    mouse.locked = not terminal.enabled
    if terminal.enabled:
        terminal.input_field.active = True

# Player
player = FirstPersonController(position=(0, 120, 0))
door_open = False
riding_bike = False
dealer_door_open = False

def input(key):
    global door_open, riding_bike, dealer_door_open
    if terminal.enabled:
        if key == 'escape': toggle_terminal()
        return

    if key == 't':
        if laptop.parent == camera:
            toggle_terminal()
            laptop_screen.shake()
        return

    if key == 'f':
        phone.toggle()
        return
        
    if phone.is_open:
        return

    if key == 'e':
        hit = mouse.hovered_entity
        holding_laptop = (laptop.parent == camera)
        
        if hit in baristas:
            if distance(player.position, hit.world_position) < 6:
                hit.speech_text.text = f"The WiFi is:\n'{hit.ssid}'"
            return
            
        if hit in (door, door_knob):
            if distance(player.position, door_pivot.world_position) < 5:
                door_open = not door_open
                door_pivot.animate_rotation_y(90 if door_open else 0, duration=0.6)
            return
                
        if hit == dealer_door or getattr(hit, 'parent', None) == dealer_door:
            if distance(player.position, dealer_door.world_position) < 10:
                dealer_door_open = not dealer_door_open
                dealer_door_pivot.animate_rotation_y(90 if dealer_door_open else 0, duration=0.6)
            return
            
        if hit in (btn_up, btn_down, call_top_btn, call_bot_btn) or (hit is None and (distance(player.position, call_top_btn.world_position) < 8 or distance(player.position, call_bot_btn.world_position) < 8)):
            if elevator.y > 60:
                elevator.animate_y(0.05, duration=15, curve=curve.in_out_quad)
            else:
                elevator.animate_y(120.0, duration=15, curve=curve.in_out_quad)
            return
            
        if hit == bicycle or getattr(hit, 'parent', None) == bicycle or getattr(getattr(hit, 'parent', None), 'parent', None) == bicycle or (distance(player.position, bicycle.world_position) < 4 and hit is None):
            riding_bike = not riding_bike
            bike_parts = [bicycle] + bicycle.children
            if riding_bike:
                player.position = bicycle.world_position + Vec3(0, 1.0, 0)
                bicycle.parent = player
                bicycle.position = Vec3(0, -0.7, 0.8) # Adjusted for better view
                bicycle.rotation = Vec3(0, -90, 0) # Flip to face forward (+Z) instead of backward
                player.speed = 25 # Boosted speed more to make it obvious
                if hasattr(player, 'ignore_list'):
                    player.ignore_list.extend(bike_parts)
            else:
                bicycle.parent = scene
                bicycle.world_position = player.position + player.forward * 1.5
                bicycle.rotation_y = player.rotation_y - 90
                bicycle.y = 0.3
                player.speed = 5
                if hasattr(player, 'ignore_list'):
                    for ent in bike_parts:
                        if ent in player.ignore_list:
                            player.ignore_list.remove(ent)
            return
            
        if not holding_laptop and (hit == laptop or hit in (laptop_base, laptop_screen, screen_glow) or getattr(hit, 'parent', None) == laptop):
            if distance(player.position, laptop.world_position) < 4:
                laptop.parent = camera
                laptop.scale = 0.3
                laptop.position = Vec3(0.6, -0.35, 1.0) 
                laptop.rotation = Vec3(15, -20, 0)
            return
            
        if holding_laptop:
            from ursina import raycast
            r = raycast(camera.world_position, camera.forward, distance=8, ignore=[player, laptop, laptop_base, laptop_screen, screen_glow, bicycle])
            if r.hit:
                laptop.parent = scene
                laptop.scale = 1
                laptop.world_position = r.world_point + Vec3(0, 0.05, 0)
                laptop.rotation = Vec3(0, player.rotation_y, 0)
            return

# --- NPCs ---
class Citizen(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=random.choice([color.red, color.blue, color.green, color.orange, color.magenta, color.yellow]),
            scale=(1, 2, 1),
            position=position,
            collider='box'
        )
        # Visual 'eye' to show facing direction
        self.eye = Entity(parent=self, model='cube', color=color.black, scale=(0.4, 0.2, 0.4), position=(0, 0.5, 0.4))
        self.speed = random.uniform(2, 5)
        self.target_pos = self.get_new_target()
        
    def get_new_target(self):
        return Vec3(random.uniform(-80, 80), 1, random.uniform(-80, 80))
        
    def update(self):
        direction = self.target_pos - self.position
        direction.y = 0
        dist = direction.length()
        
        if dist < 1:
            self.target_pos = self.get_new_target()
        else:
            direction = direction.normalized()
            self.position += direction * self.speed * time.dt
            self.look_at(self.position + direction)
            self.rotation = Vec3(0, self.rotation_y, 0)

npcs = [Citizen(Vec3(random.uniform(-80, 80), 1, random.uniform(-80, 80))) for _ in range(25)]

class GreeterNPC(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.cyan,
            scale=(1.2, 2.0, 1.2),
            position=(9, 1.0, 14),
            collider='box'
        )
        self.head = Entity(parent=self, model='sphere', color=color.white, scale=0.8, position=(0, 0.8, 0))
        Text(parent=self, text='Welcome to the city!\nUse the yellow pillar\nto call the elevator!', scale=3, position=(0, 1.8, 0), billboard=True, color=color.yellow, origin=(0, 0))

greeter = GreeterNPC()
greeter.look_at(Vec3(0, 1.0, 0)) # Look generally towards the open area

cops = []

class Cop(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.rgb(0.1, 0.2, 0.8),
            scale=(1.1, 2.0, 1.1),
            position=position,
            collider='box'
        )
        self.head = Entity(parent=self, model='sphere', color=color.rgb(1, 0.8, 0.6), scale=0.8, position=(0, 0.8, 0))
        self.hat = Entity(parent=self.head, model='cube', color=color.black, scale=(1.2, 0.3, 1.2), position=(0, 0.4, 0))
        self.hat_bill = Entity(parent=self.hat, model='cube', color=color.black, scale=(0.8, 0.1, 1.5), position=(0, -0.1, 0.4))
        self.speed = 10

        self.is_active = True
        self.speech = Text(parent=self, text='STOP RIGHT THERE!', scale=3, position=(0, 2.5, 0), billboard=True, color=color.red, origin=(0, 0))

    def update(self):
        if not self.is_active: return
        
        dist_3d = distance(player.position, self.position)
        if dist_3d < 3.0:
            self.arrest_player()
            return
            
        if dist_3d > 120.0:
            self.is_active = False
            self.speech.text = 'Lost the suspect! RTB.'
            self.speech.color = color.light_gray
            invoke(self.cleanup, delay=3.0)
            return
            
        direction = player.world_position - self.position
        direction.y = 0
        if direction.length() > 0.1:
            direction = direction.normalized()
            self.position += direction * self.speed * time.dt
            self.look_at(self.position + direction)
            self.rotation = Vec3(0, self.rotation_y, 0)
            self.y = 1.0
            
    def arrest_player(self):
        self.is_active = False
        global player_money
        player_money = max(0, player_money - 2000)
        money_text.text = f"${player_money}"
        
        if terminal.enabled:
            toggle_terminal()
            
        player.position = Vec3(0, 120, 0)
        
        self.speech.text = 'BUSTED! Fine: $2000'
        invoke(self.cleanup, delay=3.0)
        
    def cleanup(self):
        if self in cops:
            cops.remove(self)
        destroy(self)

wanted_level = 0.0
wanted_text = Text(text="⚠️ CAFE STAFF IS SUSPICIOUS ⚠️", position=(0, 0.35), color=color.red, scale=2, origin=(0, 0), enabled=False)

def update():
    global wanted_level
    
    if terminal.enabled:
        is_sus = False
        for b in baristas:
            if distance(player.position, b.world_position) < 22:
                is_sus = True
                wanted_level += time.dt
                if wanted_level > 0:
                    wanted_text.enabled = True
                    time_left = max(0.0, 7.0 - wanted_level)
                    wanted_text.text = f"⚠️ STAFF SUSPICIOUS: {time_left:.1f}s ⚠️"
                
                if wanted_level > 7.0:
                    b.speech_text.text = "POLICE!!\nWE HAVE A HACKER!"
                    b.speech_text.color = color.red
                    if len(cops) < 2:
                        dx = random.choice([-1, 1]) * random.uniform(60, 100)
                        dz = random.choice([-1, 1]) * random.uniform(60, 100)
                        spawn_pos = player.world_position + Vec3(dx, 0, dz)
                        cops.append(Cop(spawn_pos))
                    wanted_level = -5.0 # Cooldown to avoid spawning infinitely
                break
        
        if not is_sus:
            wanted_level = max(0, wanted_level - time.dt)
            if wanted_level <= 0.0:
                wanted_text.enabled = False
    else:
        wanted_level = max(0, wanted_level - time.dt)
        if wanted_level <= 0.0:
            wanted_text.enabled = False

    screen_glow.color = color.rgba(0, 255, 0, 160 + random.randint(0, 80))
    # Elevator riding logic
    if not hasattr(elevator, 'last_y'):
        elevator.last_y = elevator.y
    
    y_diff = elevator.y - elevator.last_y
    if abs(y_diff) > 0.0001:
        # Check if player is on the elevator
        dist_x = abs(player.x - elevator.x)
        dist_z = abs(player.z - elevator.z)
        
        if dist_x < 1.3 and dist_z < 1.3:
            # Player is within elevator bounds XZ
            # Check if they are on the floor (with a small margin)
            if elevator.y - 0.5 < player.y < elevator.y + 1.0:
                player.y += y_diff
                
    elevator.last_y = elevator.y


Text(text='[WASD] Move  [E] Action / Press Buttons  [F] Phone  [ESC] Exit', position=(-0.85, 0.48), color=color.gray)

app.run()
