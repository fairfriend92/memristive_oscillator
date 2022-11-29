import numpy as np
import matplotlib.pyplot as plt

Rlow    =   0.5     # Low resistance 
Rhig    =   10.     # High resistance
Rload   =   2.0     # Load resistance
i1      =   1.0     # Current value at the beginning of the NDR
i2      =   3.0     # Current value at the end of the NDR 
i3      =   10.     # Final current value
di      =   .05     # Current step
v3      =   80.     # Final voltage value
dv      =   .05     # Voltage step
dt      =   .1      # Time step
C       =   .1      # Capacitance

vCtrl   =   False    # Voltage-controlled regime

def addPad(x, y):
    lenX    = len(x)
    lenY    = len(y)
    pad     = np.zeros(np.abs(lenX-lenY))
    if lenX > lenY:
        y = np.concatenate((y, pad))        
    else:
        x = np.concatenate((x, pad))
    return x, y

def doFig(x, y, xSize, ySize, labelSize, path, 
          color='black', xLabel='none', yLabel='none',
          xLimLeft=None, xLimRight=None, 
          yLimBottom=None, yLimTop=None,
          title='none', markerStyle=''):          
    fig, ax = plt.subplots(figsize=(xSize, ySize))
    ax.plot(x, y, color, marker=markerStyle)
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
        #return Rlow/(1 + (i-i2))
        return Rlow
    else:    
        return Rhig + (i-i1)*(Rhig-Rlow)/(i1-i2)
        
def doIV():
    rArr    = []
    vArr    = []  
    maxV    = 0.
    j       = 0
    
    iArr            = np.arange(0., i3, di)
    vAppArr         = np.arange(0., v3, dv)
    inptLen         = len(vAppArr) if vCtrl else len(iArr)
    vAppArr, iArr   = addPad(vAppArr, iArr)

    for i, vApp in zip(iArr, vAppArr):
        if j >= inptLen:
            break
    
        if vCtrl is True:
            rOld    = Rhig if len(rArr) == 0 else rArr[-1]   
            vLoad   = vApp*Rload/(rOld + Rload)
            i       = vLoad/Rload
            iArr[j] = i
            
        r       = getR(i)
        v       = i*r
        j       = j+1
        maxV    = v if v > maxV else maxV
        
        rArr.append(r)
        vArr.append(v) 
        
    doFig(iArr[:inptLen], rArr, 8, 6, 22, './figures/R(I).pdf',
          'black', 'Current (arb. units)', 'Resistance (arb. units)',
          0., i3, 0., Rhig+1., markerStyle='.')
    doFig(vArr, iArr[:inptLen], 8, 6, 22, './figures/IV.pdf',
          'black', 'Voltage (arb. units)', 'Current (arb. units)',
          0., maxV+1., 0., i3, markerStyle='.')
          
def doOscill(iArr, vAppArr, vOld, rOld, doPrint = True):
    icArr   = []    # Capacitor current
    ixArr   = []    # Memristor current
    rArr    = []    # Memristor resistance
    vArr    = []    # Voltage of memristor and capacitor    
    j       = 0
    
    for i, vApp in zip(iArr, vAppArr): 
        if j >= inptLen:
            break
            
        if vCtrl is True:
            vLoad   = vApp*Rload/(rOld + Rload)
            i       = vLoad/Rload
            iArr[j] = i
        
        ix      = (vOld + i*dt/C)/(rOld + dt/C)
        ic      = i - ix
        r       = getR(ix)
        v       = vOld + ic*dt/C
        rOld    = r
        vOld    = v
        j       = j+1
        
        icArr.append(ic)
        ixArr.append(ix)
        rArr.append(r)
        vArr.append(v)
    
    if doPrint:
        if vCtrl is  True:
            tArr    = range(0, len(vAppArr))
            iOld    = icArr[-1]+ixArr[-1]
            title   = r'$I_{tot}=$'+str(np.round(iOld,2))
            name    = 'i='+str(np.round(iOld,2))
            '''
            title   = r'$V_{app}=$'+str(np.round(vAppArr[-1],2))
            name    = 'vApp='+str(np.round(vAppArr[-1],2))
            '''
        else:
            tArr    = range(0, len(iArr))
            iOld    = iArr[-1]
            title   = r'$I_{tot}=$'+str(np.round(iArr[-1],2))
            name    = 'i='+str(np.round(iArr[-1],2))
       
        '''
        doFig(tArr, ixArr, 8, 6, 22, './figures/Ix(t)_'+name+'.pdf',
              'black', 'Time (arb. units)', r'$I_X$' + '(arb. units)',
              0, tArr[-1], None, None, title)
        
        doFig(tArr, icArr, 8, 6, 22, './figures/Ic(t)_'+name+'.pdf',
              'black', 'Time (arb. units)', r'$I_C$' + '(arb. units)',
              0, tArr[-1], None, None, title)
        doFig(tArr, vArr, 8, 6, 22, './figures/V(t)_'+name+'.pdf',
              'black', 'Time (arb. units)', 'Voltage (arb. units)',
              0, tArr[-1], None, None, title) 
        doFig(tArr, rArr, 8, 6, 22, './figures/R(t)_'+name+'.pdf',
              'black', 'Time (arb. units)', 'Resistance (arb. units)',
              0, tArr[-1], None, None, title)
        '''
         
    return vOld, rOld, iOld

# Main loop #
        
doIV()

# Oscillatory regime input
vAppArr         = np.arange(0., 25., dv)
iArr            = np.arange(0., 5., di)
inptLen         = len(vAppArr) if vCtrl else len(iArr)
vAppArr, iArr   = addPad(vAppArr, iArr)

vArr    = []
T       = 1000
vOld    = 0.
rOld    = Rhig
j       = 0   

for i, vApp in zip(iArr, vAppArr):
    if j >= inptLen:
        break
        
    print(str(np.round(float(100*j/inptLen),1))+"%")
    vOld, rOld, iOld    = doOscill(i*np.ones(T), vApp*np.ones(T), vOld, Rhig, True)
    if vCtrl is True:
        iArr[j] = iOld  
    j   = j+1
    
    vArr.append(vOld)

doFig(iArr[:inptLen], vArr, 8, 6, 22, './figures/IV_oscill.pdf',
      'black', 'Current (arb. units)', 'Voltage (arb. units)',
      0, iArr[inptLen-1], 0, None, markerStyle='.')

