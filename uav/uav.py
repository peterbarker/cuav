from numpy import array, linalg, eye, zeros, dot
from numpy import sin, cos, pi
from matplotlib import pyplot

def rotationMatrix(phi, theta, psi):
  out = zeros((3,3))
  out[0,0] = cos(psi)*cos(theta)
  out[0,1] = cos(psi)*sin(theta)*sin(phi) - sin(psi)*cos(phi)
  out[0,2] = cos(psi)*sin(theta)*cos(phi) + sin(psi)*sin(phi)

  out[1,0] = sin(psi)*cos(theta)
  out[1,1] = sin(psi)*sin(theta)*sin(phi) + cos(psi)*cos(phi)
  out[1,2] = sin(psi)*sin(theta)*cos(phi) - cos(psi)*sin(phi)

  out[2,0] = -sin(theta)
  out[2,1] = cos(theta)*sin(phi)
  out[2,2] = cos(theta)*cos(phi)

  return out


class uavxfer:
  
  def setCameraParams(self, fu, fv, cu, cv):
    K  = array([[fu, 0.0, cu],[0.0, fv, cv],[0.0, 0.0, 1.0]])
    K_i = linalg.inv(K)
    self.Tk = eye(4,4)
    self.Tk[:3,:3] = K;
    self.Tk_i = eye(4,4)
    self.Tk_i[:3,:3] = K_i

  def setCameraOrientation(self, roll, pitch, yaw):
    self.Rc = array(eye(4,4))
    self.Rc[:3,:3] = rotationMatrix(roll, pitch, yaw)
    self.Rc_i = linalg.inv(self.Rc)

  def setPlatformPose(self, north, east, down, roll, pitch, yaw):
    self.Rp = array(eye(4,4))
    self.Rp[:3,:3] = rotationMatrix(roll, pitch, yaw)
    self.Rp[:3,3] = array([north, east, down])
    self.Rp_i = linalg.inv(self.Rp)

  def setFlatEarth(self, z):
    self.z_earth = z

  def worldToPlatform(self, north, east, down):
    x_w = array([north, east, down, 1.0])
    x_p = dot(self.Rp_i, x_w)[:3]
    return x_p

  def worldToImage(self, north, east, down):
    x_w = array([north, east, down, 1.0])
    x_p = dot(self.Rp_i, x_w)
    x_c = dot(self.Rc_i, x_p)
    x_i = dot(self.Tk, x_c)
    return x_i[:3]/x_i[2]

  def platformToWorld(self, north, east, down):
    x_p = array([north, east, down, 1.0])
    x_w = dot(self.Rp, x_p)
    return x_w

  def imageToWorld(self, u, v):
    x_i = array([u, v, 1.0, 0.0])
    print 'x_i', x_i
    x_c = dot(self.Tk_i, x_i)
    print 'x_c', x_c
    x_p = dot(self.Rc, x_c)
    print 'x_p', x_p
    x_w = dot(self.Rp, x_p)
    x_w = self.z_earth*x_w/x_w[2]
    print 'x_w', x_w
    return x_w

  def __init__(self, fu=200, fv=200, cu=512, cv=480):
    self.setCameraParams(fu, fv, cu, cv)
    self.Rc = self.Rc_i = array(eye(4,4))
    self.Rp = self.Rp_i = array(eye(4,4))
    self.z_earth = -600


if __name__ == '__main__':
  xfer = uavxfer()
  xfer.setCameraParams(200.0, 200.0, 512, 480)
  xfer.setCameraOrientation(0.0, 0.0, pi/2)
  xfer.setPlatformPose(500.0, 1000.0, -700.0, 0.00, 0.00, pi/2)

  f = pyplot.figure(1)
  f.show()

  p_w = array([500. +00., 1000. -00., -600.0])
  p_p = xfer.worldToPlatform(p_w[0], p_w[1], p_w[2])
  p_i = xfer.worldToImage(p_w[0], p_w[1], p_w[2])

  pyplot.plot(p_w[1], -p_w[0], 'bo')
  pyplot.plot(p_p[1], -p_p[0], 'ro')

  l_w = xfer.imageToWorld(p_i[0], p_i[1])

  print l_w
