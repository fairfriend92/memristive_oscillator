import numpy as np
import matplotlib.pyplot as plt

Rlow    =   0.5     # Low resistance 
Rhig    =   10.     # High resistance
Rload   =   2.0     # Load resistance
i1      =   1.0     # Current value at the beginning of the NDR
i2      =   3.0     # Current value at the end of the NDR 
i3      =   10.     # Final current value
di      =   .01     # Current step
dt      =   0.1     # Time step
C       =   0.1     # Capacitance

def doFig(x, y, xSize, ySize, labelSize, path, 
          color='black', xLabel='none', yLabel='none',
          xLimLeft=None, xLimRight=None, 
          yLimBottom=None, yLimTop=None,
          title='none'):          
    fig, ax = plt.subplots(figsize=(xSize, ySize))
    ax.plot(x, y, color)
    ax.set(xlabel=xLabel, ylabel=yLabel)
    ax.xaxis.label.set_size(labelSize)
    ax.yaxis.label.set_size(labelSize)
    
    if yLimBottom is not None:
        ax.set_ylim(bottom=yLimBottom)
    if yLimTop is not None:
        ax.set_ylim(top=yLimTop)
    if xLimLeft is not None:
        ax.set_xlim(left=xLimLeft)
    if xLimRight is not None:
        ax.set_xlim(right=xLimRight)
        
    ax.tick_params(axis='both', which='both', labelsize=labelSize, length=int(labelSize/6))    
    if title != 'none':
        plt.title(title, {'fontsize': labelSize})
    fig.tight_layout()
    plt.savefig(path) 
    plt.close()
          

def getR(i):
    if i <= i1:
        return Rhig
    elif i >= i2:
        return Rlow
    else:    
        return Rhig + (i-i1)*(Rhig-Rlow)/(i1-i2)
        
def doIV():
    iArr    = np.arange(0., i3, di)
    rArr    = []
    vArr    = []  
    maxV    = 0.
    for i in iArr:
        r = getR(i)
        rArr.append(r)
        
        v = i*r
        maxV = v if v > maxV else maxV
        vArr.append(v)    
    doFig(iArr, rArr, 8, 6, 22, './figures/R(I).pdf',
          'black', 'Current (arb. units)', 'Resistance (arb. units)',
          0., i3, 0., Rhig+1.)
    doFig(vArr, iArr, 8, 6, 22, './figures/IV.pdf',
          'black', 'Voltage (arb. units)', 'Current (arb. units)',
          0., maxV+1., 0., i3)
          
def doOscill(iArr, vOld, rOld):
    icArr   = []    # Capacitor current
    ixArr   = []    # Memristor current
    rArr    = []    # Memristor resistance
    vArr    = []    # Voltage of memristor and capacitor
        
    for i in iArr: 
        ix      = (vOld + i*dt/C)/(rOld + dt/C)
        ic      = i - ix
        r       = getR(ix)
        v       = vOld + ic*dt/C
        rOld    = r
        vOld    = v
        
        icArr.append(ic)
        ixArr.append(ix)
        rArr.append(r)
        vArr.append(v)
    tArr = range(0, len(iArr))   
    
    iStr = str(np.round(iArr[-1],2))
    doFig(tArr, ixArr, 8, 6, 22, './figures/Ix(t)_i='+iStr+'.pdf',
          'black', 'Time (arb. units)', r'$I_X$' + '(arb. units)',
          0, tArr[-1], None, None, r'$I_{tot}=$'+iStr)
    doFig(tArr, icArr, 8, 6, 22, './figures/Ic(t)_i='+iStr+'.pdf',
          'black', 'Time (arb. units)', r'$I_C$' + '(arb. units)',
          0, tArr[-1], None, None, r'$I_{tot}=$'+iStr)
    doFig(tArr, vArr, 8, 6, 22, './figures/V(t)_i='+iStr+'.pdf',
          'black', 'Time (arb. units)', 'Voltage (arb. units)',
          0, tArr[-1], None, None, r'$I_{tot}=$'+iStr) 
    doFig(tArr, rArr, 8, 6, 22, './figures/R(t)_i='+iStr+'.pdf',
          'black', 'Time (arb. units)', 'Resistance (arb. units)',
          0, tArr[-1], None, None, r'$I_{tot}=$'+iStr)
          
    return vOld, rOld
        
doIV()

T       = 1000

di      = 0.1
iArr    = np.arange(0., 5., di)
vOld    = 0.
rOld    = Rhig
for i in iArr:
    vOld, rOld = doOscill(i*np.ones(T), vOld, Rhig)

#doOscill(2.5*np.ones(T), 0., Rhig)