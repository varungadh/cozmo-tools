from math import pi, inf, sin, cos, atan2, sqrt
from cozmo.faces import Face
from cozmo.objects import LightCube, CustomObject, EvtObjectMovingStopped

from . import transform
from . import custom_objs
from .transform import wrap_angle

class WorldObject():
    def __init__(self, id=None, x=0, y=0, z=0, is_visible=None):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.obstacle = True
        if is_visible is not None:
            self.is_visible = is_visible
        self.sdk_obj = None
        self.update_from_sdk = False
        self.is_foreign = False
        if is_visible:
            self.pose_confidence = +1
        else:
            self.pose_confidence = -1

class LightCubeObj(WorldObject):
    light_cube_size = (44., 44., 44.)
    def __init__(self, sdk_obj, id=None, x=0, y=0, z=0, theta=0):
        super().__init__(id,x,y,z)
        self.sdk_obj = sdk_obj
        self.update_from_sdk = True
        self.theta = theta
        self.size = self.light_cube_size

    @property
    def is_visible(self):
        return self.sdk_obj.is_visible

    def __repr__(self):
        if self.pose_confidence >= 0:
            return '<LightCubeObj %d: (%.1f, %.1f, %.1f) @ %d deg.>' % \
                (self.id, self.x, self.y, self.z, self.theta*180/pi)
        else:
            return '<LightCubeObj %d: position unknown>' % self.id


class ChargerObj(WorldObject):
    def __init__(self, sdk_obj, id=None, x=0, y=0, z=0, theta=0):
        super().__init__(id,x,y,z)
        self.sdk_obj = sdk_obj
        self.update_from_sdk = True
        self.theta = theta
        self.size = (104, 98, 10)

    @property
    def is_visible(self):
        return self.sdk_obj.is_visible

    def __repr__(self):
        if self.pose_confidence >= 0:
            return '<ChargerObj: (%.1f, %.1f, %.1f) @ %d deg.>' % \
                (self.x, self.y, self.z, self.theta*180/pi)
        else:
            return '<ChargerObj: position unknown>'

class CustomMarkerObj(WorldObject):
    def __init__(self, id=None, x=0, y=0, z=0, theta=0):
        super().__init__(id,x,y,z)
        self.theta = theta
        self.sdk_obj = id

    @property
    def is_visible(self):
        return self.sdk_obj.is_visible

    def __repr__(self):
        return '<CustomMarkerObj %d: (%.1f,%.1f)>' % \
               (self.id.object_id, self.x, self.y)

class CustomCubeObj(WorldObject):
    def __init__(self, sdk_obj, id=None, x=0, y=0, z=0, theta=0, size=None):
        # id is a CustomObjecType
        super().__init__(id,x,y,z)
        self.sdk_obj = sdk_obj
        self.update_from_sdk = True
        self.theta = theta
        if (size is None) and isinstance(id, CustomObject):
            self.size = (id.x_size_mm, id.y_size_mm, id.z_size_mm)
        elif size:
            self.size = size
        else:
            self.size = (50., 50., 50.)

    @property
    def is_visible(self):
        return self.sdk_obj.is_visible

    def __repr__(self):
        return '<CustomCubeObj %s: (%.1f,%.1f, %.1f) @ %d deg.>' % \
               (self.sdk_obj.object_type, self.x, self.y, self.z, self.theta*180/pi)

class ArucoMarkerObj(WorldObject):
    # *** TODO: is_visible should be computed dynamically
    def __init__(self, aruco_parent, id=None, x=0, y=0, z=0, theta=0):
        super().__init__(id,x,y,z)
        self.aruco_parent = aruco_parent
        self.theta = theta

    @property
    def is_visible(self):
        return self.id in self.aruco_parent.seen_marker_ids

    def __repr__(self):
        return '<ArucoMarkerObj %d: (%.1f,%.1f)>' % \
               (self.id, self.x, self.y)

class WallObj(WorldObject):
    def __init__(self, id=None, x=0, y=0, theta=0, length=100, height=150,
                 door_width=75, door_height=105, markers=[], door_ids=[], is_foreign=False):
        super().__init__(id,x,y,is_visible=False)
        self.z = height/2
        self.theta = theta
        self.length = length
        self.height = height
        self.door_width = door_width
        self.door_height = door_height
        self.markers = markers
        self.door_ids = door_ids
        self.is_foreign = is_foreign

    def update(self,x=0, y=0, theta=0):
        # Used instead of making new object for efficiency
        self.x = x
        self.y = y
        self.theta = theta

    def __repr__(self):
        return '<WallObj %d: (%.1f,%.1f) @ %d deg. for %.1f>' % \
               (self.id, self.x, self.y, self.theta*180/pi, self.length)

class ChipObj(WorldObject):
    def __init__(self, id, x, y, z=0, radius=25/2, thickness=4):
        super().__init__(id,x,y,z)
        self.radius = radius
        self.thickness = thickness

    def __repr__(self):
        return '<ChipObj (%.1f,%.1f) radius %.1f>' % \
               (self.x, self.y, self.radius)

class FaceObj(WorldObject):
    def __init__(self, sdk_obj, id, x, y, z, name):
        super().__init__(id, x, y, z)
        self.sdk_obj = sdk_obj
        self.obstacle = False

    @property
    def name(self):
        return self.sdk_obj.name

    @property
    def is_visible(self):
        return self.sdk_obj.is_visible

    def __repr__(self):
        return "<FaceObj name:'%s' expr:%s (%.1f, %.1f, %.1f) vis:%s>" % \
               (self.name, self.expression, self.x, self.y, self.z, self.is_visible)


class CameraObj(WorldObject):
    camera_size = (44., 44., 44.)
    def __init__(self, id=None, x=0, y=0, z=0, theta=0, phi = 0):
        super().__init__(id,x,y,z)
        self.size = self.camera_size
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.phi = phi

    def update(self,x=0, y=0, z=0, theta = 0, phi = 0):
        # Used instead of making new object for efficiency
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.phi = phi

    def __repr__(self):
        return '<CameraObj %d: (%.1f, %.1f, %.1f) @ %f.>\n' % \
               (self.id, self.x, self.y, self.z, self.phi*180/pi)

class RobotForeignObj(WorldObject):
    def __init__(self, cozmo_id=None, x=0, y=0, z=0, theta=0, camera_id = -1 ):
        super().__init__(id,x,y,z)
        self.cozmo_id = cozmo_id
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.size = (120., 90., 100.)
        self.camera_id = camera_id

    def __repr__(self):
        return '<RobotForeignObj %d: (%.1f, %.1f, %.1f) @ %f.> from camera %f\n' % \
               (self.cozmo_id, self.x, self.y, self.z, self.theta*180/pi, self.camera_id)

    def update(self, x=0, y=0, z=0, theta=0, camera_id=-1):
        # Used instead of making new object for efficiency
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.camera_id = camera_id


class LightCubeForeignObj(WorldObject):
    light_cube_size = (44., 44., 44.)
    def __init__(self, id=None, cozmo_id=None, x=0, y=0, z=0, theta=0, is_visible=False):
        super().__init__(id,x,y,z)
        self.theta = theta
        self.cozmo_id = cozmo_id
        self.size = self.light_cube_size
        self.is_visible = is_visible

    def __repr__(self):
        return '<LightCubeForeignObj %d: (%.1f, %.1f, %.1f) @ %d deg.> by cozmo %d \n' % \
               (self.id, self.x, self.y, self.z, self.theta*180/pi, self.cozmo_id)

    def update(self, x=0, y=0, z=0, theta=0):
        # Used instead of making new object for efficiency
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta


#================ WorldMap ================

class WorldMap():
    vision_z_fudge = 10  # Cozmo underestimates object z coord by about this much

    def __init__(self,robot):
        self.robot = robot
        self.objects = dict()
        self.shared_objects = dict()
        
    def update_map(self):
        """Called to update the map just before the path planner runs.  Cubes,
        custom objects, and faces are updated automatically in reponse
        to observation events, but we update them here to get the
        freshest possible value.  Walls and Cameras are updated from
        landmarks."""
        self.update_walls()
        self.update_perched_cameras()
        if self.robot.world.charger: self.update_charger()
        for (id,cube) in self.robot.world.light_cubes.items():
            self.update_cube(cube)
        for face in self.robot.world._faces.values():
            self.update_face(face)

    def update_cube(self, cube):
        if cube in self.objects:
            if "LightCubeForeignObj-"+str(cube.cube_id) in self.objects:
                # remove foreign cube when local cube seen
                del self.objects["LightCubeForeignObj-"+str(cube.cube_id)]
            wmobject = self.objects[cube]
            if self.robot.carrying is wmobject:
                if cube.is_visible: # we thought we were carrying it, but we're wrong
                    self.robot.carrying = None
                    return self.update_cube(cube)
                else:  # we do appear to be carrying it
                    self.update_carried_object(wmobject)
        elif cube.pose is None:  # not in contact with cube
            return None
        else:
            # Cube is not in the worldmap, so add it.
            id = tuple(key for (key,value) in self.robot.world.light_cubes.items() if value == cube)[0]
            wmobject = LightCubeObj(cube, id)
            self.objects[cube] = wmobject
            if not cube.pose.is_comparable(self.robot.pose):
                wmobject.update_from_sdk = False
                wmobject.pose_confidence = -1
        if cube.is_visible:
            wmobject.update_from_sdk = True  # In case we've just dropped it; now we see it
            wmobject.pose_confidence = +1
        if wmobject.update_from_sdk:  # True unless if we've dropped it and haven't seen it yet
            self.update_coords(wmobject, cube)
        return wmobject

    def update_charger(self):
        charger = self.robot.world.charger
        if charger in self.objects:
            wmobject = self.objects[charger]
        else:
            wmobject = ChargerObj(charger)
            self.objects[charger] = wmobject
            if not charger.pose.is_comparable(self.robot.pose):
                wmobject.update_from_sdk = False
                wmobject.pose_confidence = -1
        if charger.is_visible:
            wmobject.update_from_sdk = True  # In case we've just dropped it; now we see it
            wmobject.pose_confidence = +1
        if wmobject.update_from_sdk:  # True unless if we've dropped it and haven't seen it yet
            self.update_coords(wmobject, charger)
        return wmobject

    def update_walls(self):
        for key, value in self.robot.world.particle_filter.sensor_model.landmarks.items():
            if isinstance(key,str) and 'Wall' in key:
                if key in self.objects and isinstance(self.objects[key], WallObj) and \
                        (not self.objects[key].is_foreign):
                    self.objects[key].update(x=value[0][0][0], y=value[0][1][0], theta=value[1])
                else:
                    id = int(key[-(len(key)-5):])
                    wall_spec = wall_marker_dict[id]
                    self.objects[key] = WallObj(id,
                                                x=value[0][0][0],
                                                y=value[0][1][0],
                                                theta=value[1],
                                                length=wall_spec.length,
                                                height=wall_spec.height,
                                                door_width=wall_spec.door_width,
                                                door_height=wall_spec.door_height,
                                                markers=wall_spec.markers,
                                                door_ids=wall_spec.door_ids,
                                                is_foreign=False)
        
    def lookup_face_obj(self,face):
        "Look up face by name, not by Face instance."
        for (key,value) in self.robot.world.world_map.objects.items():
            if isinstance(key, Face) and key.name == face.name:
                if key is not face and face.is_visible:
                    # Older Face object with same name: replace it with new one
                    self.robot.world.world_map.objects.pop(key)
                    self.robot.world.world_map.objects[face] = value
                return value
        return None

    def update_face(self,face):
        if face.pose is None:
            return
        pos = face.pose.position
        face_obj = self.lookup_face_obj(face)
        if face_obj is None:
            face_obj = FaceObj(face, face.face_id, pos.x, pos.y, pos.z,
                               face.name)
            self.robot.world.world_map.objects[face] = face_obj
        # now update the face
        if face.is_visible:
            face_obj.x = pos.x
            face_obj.y = pos.y
            face_obj.z = pos.z
            face_obj.expression = face.expression
            self.update_coords(face_obj, face)

    def update_custom_object(self, sdk_obj):
        if not sdk_obj.pose.is_comparable(self.robot.pose):
            print('Should never get here:',sdk_obj.pose,self.robot.pose)
            return
        if sdk_obj in self.objects:
            wmobject = self.objects[sdk_obj]
        else:
            id = sdk_obj.object_type
            if id in custom_objs.custom_marker_types:
                wmobject = CustomMarkerObj(sdk_obj,id)
            elif id in custom_objs.custom_cube_types:
                wmobject = CustomCubeObj(sdk_obj,id)
            self.objects[sdk_obj] = wmobject
        self.update_coords(wmobject, sdk_obj)

    def update_carried_object(self, wmobject):
        #print('Updating carried object ',wmobject)
        # set x,y based on robot's pose
        # need to cache initial orientation relative to robot:
        #   grasped_orient = wmobject.theta - robot.pose.rotation.angle_z
        world_frame = self.robot.kine.joints['world']
        lift_attach_frame = self.robot.kine.joints['lift_attach']
        tmat = self.robot.kine.base_to_link(world_frame).dot(self.robot.kine.joint_to_base(lift_attach_frame))
        # *** HACK *** : width calculation only works for cubes; need to handle custom obj, chips
        half_width = 22 # wmobject.size[0] / 2
        new_pose = tmat.dot(transform.point(half_width,0))
        theta = self.robot.world.particle_filter.pose[2]
        wmobject.x = new_pose[0,0]
        wmobject.y = new_pose[1,0]
        wmobject.z = new_pose[2,0]
        wmobject.theta = theta

    def update_coords(self, wmobject, sdk_obj):
        dx = sdk_obj.pose.position.x - self.robot.pose.position.x
        dy = sdk_obj.pose.position.y - self.robot.pose.position.y
        alpha = atan2(dy,dx) - self.robot.pose.rotation.angle_z.radians
        r = sqrt(dx*dx + dy*dy)
        (rob_x,rob_y,rob_theta) = self.robot.world.particle_filter.pose
        wmobject.x = rob_x + r * cos(alpha + rob_theta)
        wmobject.y = rob_y + r * sin(alpha + rob_theta)
        wmobject.z = sdk_obj.pose.position.z
        orient_diff = wrap_angle(rob_theta - self.robot.pose.rotation.angle_z.radians)
        wmobject.theta = wrap_angle(sdk_obj.pose.rotation.angle_z.radians + orient_diff)

    def update_perched_cameras(self):
        if self.robot.world.server.started:
            for key, val in self.robot.world.server.camera_landmark_pool.get(self.robot.aruco_id,{}).items():
                if isinstance(key,str) and 'Video' in key:
                    if key in self.objects:
                        self.objects[key].update(x=val[0][0,0], y=val[0][1,0], z=val[1][0],
                                                 theta=val[1][2], phi=val[1][1])
                    else:
                        # last digit of capture id as camera key
                        self.objects[key]=CameraObj(id=int(key[-2]), x=val[0][0,0], y=val[0][1,0],
                                                z=val[1][0], theta=val[1][2], phi=val[1][1])
        else:
            for key, val in self.robot.world.particle_filter.sensor_model.landmarks.items():
                if isinstance(key,str) and 'Video' in key:
                    if key in self.objects:
                        self.objects[key].update(x=val[0][0,0], y=val[0][1,0], z=val[1][0],
                                                 theta=val[1][2], phi=val[1][1])
                    else:
                        # last digit of capture id as camera key
                        self.objects[key]=CameraObj(id=int(key[-2]), x=val[0][0,0], y=val[0][1,0],
                                                z=val[1][0], theta=val[1][2], phi=val[1][1])

#================ Event Handlers ================

    def handle_object_observed(self, evt, **kwargs):
        if isinstance(evt.obj, LightCube):
            self.update_cube(evt.obj)
        elif isinstance(evt.obj, CustomObject):
            self.update_custom_object(evt.obj)
        elif isinstance(evt.obj, Face):
            self.update_face(evt.obj)

    def handle_object_moved(self, evt, **kwargs):
        cube = evt.obj
        if self.robot.carrying and self.robot.carrying.sdk_obj is cube:
            pass
        else:
            # print(evt, kwargs)
            if cube in self.robot.world.world_map.objects:
                wmobject = self.robot.world.world_map.objects[cube]
                if self.robot.carrying is wmobject: return
                if cube.is_visible:
                    wmobject.pose_confidence = +1
                else:
                    if isinstance(evt, EvtObjectMovingStopped) and \
                       evt.move_duration > 1:
                        wmobject.pose_confidence = -1
                    else:
                        wmobject.pose_confidence = min(0, wmobject.pose_confidence)


#================ Wall Specification  ================

wall_marker_dict = dict()

class WallSpec():
    def __init__(self, length=100, height=210, door_width=75, door_height=105,
                 markers={}, doorways=[], door_ids=[]):
        self.length = length
        self.height = height
        self.door_width = door_width
        self.door_height = door_height
        self.markers = markers
        self.doorways = doorways
        self.door_ids = door_ids
        ids = list(markers.keys())
        self.id = min(ids)
        global wall_marker_dict
        for id in ids:
            wall_marker_dict[id] = self

