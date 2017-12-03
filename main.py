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
          if (len(dictionary) == 65536):
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
        for x in range(img.shape[1]):
          #if (img[y,x,c] != 255):
          #  print "dictionary index: " + str(entry_num)
          #  print "dimensions: " + "[" + str(y) + "," + str(x) + "," + str(c) + "]" + " = " + str(img[y,x,c])
          #  raw_input()
          if (x-1 < 0):
            #calculate pixel value using predictive encoding and cast to an ASCII character
            #currently using the absolute value to avoid typecasting errors to ASCII character
            #pixel = chr(abs(img[y,x,c]-img[y,0,c]))
            pixel = str(img[y,x,c])
          else:
            #last pixel within range
            #pixel = chr(abs(img[y,x,c]-img[y,x-1,c]))
            pixel = str(img[y,x,c])
            #if (img[y,x,c] != 255):
            #  print (str(img[y,x,c]))
            #  raw_input()
          entry = subsequence + pixel
          #print "entry: " + entry
          if (entry in dictionary): #check if dictionary entry exists
            subsequence = entry
          else :
            output = dictionary[str(subsequence)]
            #print "dictionary["+subsequence+"]"+"="+str(output)
            #print "pixel: " + str(pixel)
            #print "output: " + str(output)
            #raw_input()
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
            if (len(dictionary) == 65536):
              #construct base dictionary
              dictionary = {}
              for i in range(0, 256):
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
  byteIter = iter(inputBytes)
  
  #construct base dictionary
  dictionary = {}
  for i in range(0, 256):
    dictionary[str(i)] = i
  #set index to start adding new entries
  entry_num = 256
  initial_entry = True;
  
  y = 0
  x = 0
  c = 0
  count = 0
    #for y in range(rows):
    #for x in range(columns):
    #for c in range(channels):
  print "y limit: " + str(rows)
  print "x limit: " + str(columns)
  print "c limit: " + str(channels)
  
  
  done = 0
  for i in byteIter:
    if (initial_entry):
      value = (i << 8) + next(byteIter)
      print "input: " + str(value)
      S = dictionary[ str(value) ]
      img[y,x,c] = S
      x+=1
      #print "code: " + str(value) + ". dictionary entry: " + str(S)
      count+=1
      initial_entry = False
    else:
      #get dictionary entry of next code
      code = str( (i << 8) + next(byteIter) )
      #print "input: " + code
      #raw_input()
      if (code in dictionary):
        #T is dictionary lookup of next code
        T = dictionary[code]
      else :
        #otherwise T is S + firstChar(S)
        T = (S << 8) + (S & 0xFF)
      #output T
      #img[y,x,c] = T
      out = T
      while (out > 0):
        img[y,x,c] = (out & 0xFF)
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
        else: 
          x+=1
        #print "output: " + str(out & 0xFF)
        if ( (out&0xFF) != 255):
          print "dictionary index: " + str(entry_num)
          print "dimensions: " + "[" + str(y) + "," + str(x) + "," + str(c) + "]" + " = " + str(out & 0xFF)
          raw_input()
        out = (out >> 8)
        count+=1
      #raw_input()
      #control indexing for y, x and c 
      #TODO
      #append S + FirstChar(T) to dictionary
      dictionary[ str((S<<8)+(T & 0xFF)) ] = entry_num
      entry_num += 1
      #if dictionary full, flush dictionary and restart
      if (len(dictionary) == 65536):
        #construct base dictionary
        dictionary = {}
        for i in range(0, 256):
          dictionary[str(i)] = i
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
