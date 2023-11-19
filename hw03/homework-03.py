import glfw
import ctypes
import OpenGL.GL as gl
import numpy as np

WINDOW_SIZE = 768
CAMERA_AXIS_SIZE = 3
ROTATION_DEG_INCREMENT = 0.5

enable_local_motion = True
enable_global_motion = False
enable_relative_motion = False

carousel_rotation_deg = 0
local_rotation_deg = 0
global_rotation_deg = 0

def init_objects():
    global carousel_rotation_deg, local_rotation_deg, global_rotation_deg
    global enable_local_motion, enable_global_motion, enable_relative_motion
        
    carousel_rotation_deg = 0
    local_rotation_deg = 0
    global_rotation_deg = 0
    enable_local_motion = False
    enable_global_motion = False
    enable_relative_motion = False

def load_obj(filename):
    vertices = []
    normals = []    
    vert_data = []
    
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '): # vertex
                vertices.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith('vn '):  # vertex normal
                normals.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith('f '):  # face
                face = line.strip().split()[1:]
                for vertex in face:
                    v_idx, _, n_idx = (map(int, vertex.replace('//', '/').split('/')))
                    vert_data.extend(vertices[v_idx-1]) # index starts from 1
                    vert_data.extend(normals[n_idx-1]) # index starts from 1
    
    vbo = gl.glGenBuffers(1)
    arr_vertices = np.array(vert_data, dtype=np.float32).flatten()
    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, arr_vertices.nbytes, arr_vertices, gl.GL_STATIC_DRAW)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    
    return vbo, len(arr_vertices)//2

def main():
    global carousel_rotation_deg, local_rotation_deg, global_rotation_deg
    
    # initialize glfw
    if not glfw.init():
        print("Glfw window can't be initialized")
        return

    window = glfw.create_window(WINDOW_SIZE, WINDOW_SIZE, "Graphics HW#3 - SkyKim", None, None)

    if not window:
        glfw.terminate()
        print("Glfw window can't be created")
        return
    
    glfw.set_window_pos(window, 0, 0)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    
    gl.glClearColor(0.0, 0.0, 0.0, 1.0) # background color is black
    print(f'OpenGL version:{gl.glGetString(gl.GL_VERSION)}')
    
    # load OBJs
    bunny_vbo, bunny_count = load_obj("./Bunny.obj")
    athena_vbo, athena_count = load_obj("./Athena.obj")
    init_objects()
    
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [1, 1, 1, 0])
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    gl.glEnable(gl.GL_DEPTH_TEST)
   
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL) #default is FILL mode    
        
    # open window and draw
    while not glfw.window_should_close(window): 
        glfw.poll_events()
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-CAMERA_AXIS_SIZE, CAMERA_AXIS_SIZE, -CAMERA_AXIS_SIZE, CAMERA_AXIS_SIZE, -CAMERA_AXIS_SIZE, CAMERA_AXIS_SIZE)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        # carousel
        gl.glPushMatrix()
        gl.glRotatef(carousel_rotation_deg, 0, 0, 1)
        
        #global: athena
        gl.glPushMatrix()
        gl.glTranslatef(-CAMERA_AXIS_SIZE/2, CAMERA_AXIS_SIZE/2, 0)
        gl.glRotatef(-carousel_rotation_deg, 0, 0, 1)
        gl.glRotatef(global_rotation_deg, 0, 0, 1)
        display_object(athena_vbo, athena_count, (1,1,1))
        gl.glPopMatrix()
        
        #local1: bunny
        gl.glPushMatrix()
        gl.glTranslatef(CAMERA_AXIS_SIZE/2, CAMERA_AXIS_SIZE/2, 0)
        gl.glRotatef(local_rotation_deg, 0, 0, 1)
        display_object(bunny_vbo, bunny_count, (1,0,0))
        gl.glPopMatrix()        
        
        #local2: bunny
        gl.glPushMatrix()    
        gl.glTranslatef(CAMERA_AXIS_SIZE/2, -CAMERA_AXIS_SIZE/2, 0)
        gl.glRotatef(local_rotation_deg, 0, 0, 1)    
        display_object(bunny_vbo, bunny_count, (0,1,0))
        gl.glPopMatrix()

        #local3: bunny
        gl.glPushMatrix()    
        gl.glTranslatef(-CAMERA_AXIS_SIZE/2, -CAMERA_AXIS_SIZE/2, 0)
        gl.glRotatef(local_rotation_deg, 0, 0, 1)
        display_object(bunny_vbo, bunny_count, (0,0,1))
        gl.glPopMatrix()
        
        gl.glPopMatrix()
                
        # degree increment
        if enable_local_motion is True:
            local_rotation_deg = local_rotation_deg + ROTATION_DEG_INCREMENT
        if enable_global_motion is True:
            global_rotation_deg = global_rotation_deg + ROTATION_DEG_INCREMENT
        if enable_relative_motion is True:
            carousel_rotation_deg = carousel_rotation_deg + ROTATION_DEG_INCREMENT

        glfw.swap_buffers(window)
        
    # terminate program    
    gl.glDeleteBuffers(1, [athena_vbo, bunny_vbo])
    terminate_window(window)

def display_object(vbo, count, color):
    stride = 24
   
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

    gl.glVertexPointer(3, gl.GL_FLOAT, stride, ctypes.c_void_p(0))
    gl.glNormalPointer(gl.GL_FLOAT, stride, ctypes.c_void_p(12))

    gl.glColor3f(*color)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, count//3)
    
    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

def key_callback(window, key, scancode, action, mods):
    global enable_local_motion, enable_global_motion, enable_relative_motion
    
    if key == glfw.KEY_P and action == glfw.PRESS:
        print("Key_P: Polygon mode")
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL) #polygon        
    elif key == glfw.KEY_W and action == glfw.PRESS:
        print("Key_W: Wireframe mode")
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE) #wireframe        
    elif key == glfw.KEY_Q and action == glfw.PRESS:
        print("Key_Q: Quit")
        terminate_window(window)
    elif key == glfw.KEY_L and action == glfw.PRESS:        
        enable_local_motion = not enable_local_motion
        print("Key_L: Local motion - " + str(enable_local_motion))
    elif key == glfw.KEY_G and action == glfw.PRESS:        
        enable_global_motion = not enable_global_motion
        print("Key_G: Global motion - " + str(enable_global_motion))
    elif key == glfw.KEY_R and action == glfw.PRESS:        
        enable_relative_motion = not enable_relative_motion
        print("Key_R: Relative motion - "+ str(enable_relative_motion))
    elif key == glfw.KEY_I and action == glfw.PRESS:
        print("Key_I: Initialize")
        init_objects()

def terminate_window(window):
    if window:
        glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()