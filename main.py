# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm


import sys, os, math, time, netpbm
import numpy as np


# Text at the beginning of the compressed file, to identify it


headerText = 'my compressed image - v1.0'



# Compress an image


def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')
  
  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.

  startTime = time.time()
  #create output array
  
  outputBytes = bytearray()
  #construct base dictionary
  dictionary = {}
  for i in range(0, 256):
    if (i < 10):
      dictionary["00"+str(i)] = i
    elif (i < 100):
      dictionary["0"+str(i)] = i
    else:
      dictionary[str(i)] = i
  #set index to start adding new entries
  entry_num = 256
  #set base subsequence
  subsequence = ''
  
  #two dimensions means only single-channeled image
  if (img.ndim <= 2):
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        if (x-1 < 0):
          #calculate pixel value using predictive encoding and cast to an ASCII character
          #currently using the absolute value to avoid typecasting errors to ASCII character
          pixel = chr(abs(img[y,x]-img[y,0]))
        else:
          #last pixel within range
          pixel = chr(abs(img[y,x]-img[y,x-1]))
        entry = subsequence + pixel
        if (entry in dictionary): #check if dictionary entry exists
          subsequence = entry
        else :
          output = dictionary[str(subsequence)]
          #assign two byteArray entries to each index written to output stream
          #assign low byte to first entry
          outputBytes.append(output & 0xFF)
          #assign high byte to second entry
          outputBytes.append((output >> 8) & 0xFF)
          #Assign s+x subsequence to new dictionary entry
          dictionary[entry] = entry_num
          #increment index of dictionary
          entry_num += 1
          #if dictionary full, flush dictionary and restart
          if (len(dictionary) == 65535):
            #construct base dictionary
            dictionary = {} 
            for i in range(0, 256):
              dictionary[chr(i)] = i
            entry_num = 256
          #assign s=x  
          subsequence = pixel;
  #handle mult-channeled case
  else :
    for c in range(img.shape[2]):
      for y in range(img.shape[0]):
        #raw_input()
        for x in range(img.shape[1]):
          #if (img[y,x,c]<10):
          #print "["+str(y)+","+str(x)+","+str(c)+"]="+str(img[y,x,c])
          #raw_input()
          if (x-1 < 0):
            #calculate pixel value using predictive encoding and cast to an ASCII character
            #currently using the absolute value to avoid typecasting errors to ASCII character
            #pixel = chr(abs(img[y,x,c]-img[y,0,c]))
            if (img[y,x,c] < 10):
              pixel = "00" + str(img[y,x,c])
            elif(img[y,x,c] <100):
              pixel = "0" + str(img[y,x,c])
            else:
              pixel = str(img[y,x,c])
          else:
            #last pixel within range
            #pixel = chr(abs(img[y,x,c]-img[y,x-1,c]))
            if (img[y,x,c] < 10):
              pixel = "00" + str(img[y,x,c])
            elif(img[y,x,c] <100):
              pixel = "0" + str(img[y,x,c])
            else:
              pixel = str(img[y,x,c])
          entry = subsequence + pixel
          #print "entry: " + entry
          if (entry in dictionary): #check if dictionary entry exists
            subsequence = entry
          else :
            output = dictionary[str(subsequence)]
            #assign two byteArray entries to each index written to output stream
            #assign high byte to first entry
            outputBytes.append((output >> 8) & 0xFF)
            #assign low byte to second entry
            outputBytes.append(output & 0xFF)
            #Assign s+x subsequence to new dictionary entry
            dictionary[entry] = entry_num
            #increment index of dictionary
            entry_num += 1
            #if dictionary full, flush dictionary and restart
            if (len(dictionary) == 65535):
              #construct base dictionary
              dictionary = {}
              for i in range(0, 256):
                if (i < 10):
                  dictionary["00"+str(i)] = i
                elif (i < 100):
                  dictionary["0"+str(i)] = i
                else:
                  dictionary[str(i)] = i
              entry_num = 256
            #assign s=x  
            subsequence = pixel;
          
  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.
  outputFile.write( '%s\n'       % headerText )
  if (img.ndim <= 2):
    outputFile.write( '%d %d\n' % (img.shape[0], img.shape[1] ) )
  else:
    outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  outputFile.write( outputBytes )
  # Print information about the compression
  if (img.ndim <= 2):
    inSize  = img.shape[0] * img.shape[1]
  else:
    inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  


# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  

  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )
  #compare with input image
  orig = netpbm.imread( "images/cortex.pnm" ).astype('uint8')
  byteIter = iter(inputBytes)
  
  #construct base dictionary
  dictionary = {}
  for i in range(0, 256):
    if (i < 10):
      dictionary[i] = "00" + str(i)
    elif (i < 100):
      dictionary[i] = "0" + str(i)
    else:
      dictionary[i] = str(i)
  #set index to start adding new entries
  entry_num = 256
  initial_entry = True;
  #starting indexes for image recreation
  y = 0
  x = 0
  c = 0
  count = 0
  for i in byteIter:
    if (initial_entry):
      value = (i << 8) + next(byteIter)
      S = dictionary[ value ]
      print "value: " + str(value)
      print "["+str(y)+","+str(x)+","+str(c)+"]="+str(img[y,x,c])+"\t"+str(orig[y,x,c])
      img[y,x,c] = int(S)
      x+=1
      initial_entry = False
    else:
      #get dictionary entry of next code
      code = (i << 8) + next(byteIter)
      #print "input: " + str(code)
      
      if (code in dictionary):
        #print "does it get here??"
        #T is dictionary lookup of next code
        T = (dictionary[code])
        fromDict=1
      else:
        #otherwise T is S + firstChar(S)
        #firstChar = int(((bin(S))[2:10]),2)
        #T = ((S << 8) + (firstChar))     
        T = S + S[0:3]
        fromDict=0
      #output T
      printC = ''
      index = 0
      for item in T:
        printC+=item
        count+=1
        if count == 3:
          img[y,x,c] = int(printC)
          #if (y==81):
          #if (orig[y,x,c] != img[y,x,c]):
            #print "OutString: " + outString
            #print "startIndex: " + str(startindex)
            #print "endIndex: " + str(endindex)
            #print "code: " + str(code) 
            #print "In dictionary?: " + str(fromDict)
            #print "S: " + S
            #print "T: " + T
            #print "["+str(y)+","+str(x)+","+str(c)+"]="+str(img[y,x,c])+"\t"+str(orig[y,x,c])
            #raw_input()
          printC = ''
          count = 0
          if (x == columns-1):
            x = 0
            if (y == rows-1):
              y = 0
              if (c == channels-1):
                done = 1#should be done
              else:
                c+=1
            else:
              y+=1
              #raw_input()
          else: 
            x+=1  
      #append S + FirstChar(T) to dictionary
      #print "dictionary["+str((S<<8)+(T & 0xFF))+"]"+"="+str(entry_num)
      #firstChar = int(((bin(T))[2:10]),2)
      #dictionary[ entry_num ] =  (S<<8)+(firstChar)
      dictionary[entry_num ] = S + T[0:3]
      entry_num += 1
      #if dictionary full, flush dictionary and restart
      if (len(dictionary) == 65535):
        #construct base dictionary
        dictionary = {}
        for i in range(0, 256):
          if (i < 10):
            dictionary[i] = "00" + str(i)
          elif (i < 100):
            dictionary[i] = "0" + str(i)
          else:
            dictionary[i] = str(i)
        entry_num = 256
      #Assign S=T
      S = T
        
  print "number of outputs is " + str(count)     
  endTime = time.time()

  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )


# The command line is 
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)
