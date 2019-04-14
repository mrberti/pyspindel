import math

MODE_INT = 1
MODE_FLOAT = 2

class PT1(object):
    def __init__(self, t_sample, tau, K=1, mode=MODE_FLOAT, shift=10):
        # TODO:
        # - Rename parameters
        self._t_sample = t_sample
        self._tau = tau
        self._mode = mode
        self._shift = shift
        if mode == MODE_INT:
            self._a0 = int(math.e**(-t_sample / tau) * (1 << shift))
            self._a1 = int((1 << shift) - self._a0)
            self._K = int(K)
        elif mode == MODE_FLOAT:
            self._a0 = math.e**(-t_sample / tau)
            self._a1 = (1 - self._a0)
            self._K = K
        else:
            raise ValueError("Mode '{}' not supported for PT1".format(mode))
        # TODO: initial state
        self._u_d = 0
        self._y_d = 0

    def step(self, u):
        y = (self._K * self._u_d * self._a1 + self._y_d * self._a0)
        if self._mode == MODE_INT:
            y >>= self._shift
        self._u_d = u
        self._y_d = y
        return y


def main():
    import matplotlib.pyplot as plt
    pt1 = PT1(.1, .5, .2)
    u_vect = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    y_vect = []
    for u in u_vect:
        y_vect.append(pt1.step(u*1))
    print(y_vect)
    plt.plot(y_vect)
    plt.show()

if __name__ == "__main__":
    main()
