# this is not the version used in the show
# the file is currently inaccessible because I'm moving
# I'll update it soon

import sounddevice
import os
import urllib.request
import numpy as np
import diskcache as dc

cache = dc.Cache('bfiles')
scale = 1<<31
def getbfile(n):
    if n in cache:
        return cache[n]
    text = urllib.request.urlopen("http://oeis.org/A{:0>6}/b{:0>6}.txt".format(n,n)).read().decode()
    text = " ".join([line for line in text.split('\n') if '#' not in line])
    cache[n] = np.array(list(map(lambda x:x%scale,map(int,text.split()[1::2]))))
    print(cache[n].shape)
    return cache[n]

x = np.zeros(0)
for i in range(1,1000):
    arr = getbfile(i)
    r = 8192#min(1024,arr.shape[0]+1)
    arrs = ((arr%r)/(r/2)-1)
    clen = 8192
    arr = np.repeat(arrs,clen//arrs.shape[0]+1)[:clen]
    x = np.append(x,arr)
n = x.shape[0]
chunkn = 1<<11
print(n,chunkn)
out = np.zeros(((n//chunkn*chunkn+chunkn)*4,2))
k = 0
#out = np.append(out,np.zeros((chunkn//2,2)),axis=0)
while True:
    j = k#//8+k%5
    i = j
    print(i,n//chunkn)
    if i >= n//chunkn:
        break
    z = (1j)**(x[i*chunkn:(i+1)*chunkn])/((1+np.arange(chunkn))**0.7)
    z = np.fft.ifft(z)
    l = abs(np.real(z))
    r = abs(np.imag(z))
    l *= np.hanning(chunkn)
    r *= np.hanning(chunkn)
    l /= np.max(l)
    r /= np.max(r)
    out[k*chunkn//2:k*chunkn//2+chunkn,0] += l-0.5
    out[k*chunkn//2:k*chunkn//2+chunkn,1] += r-0.5
    k += 1
sounddevice.play(out,44100)
sounddevice.wait()
