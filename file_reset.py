with open('Vaccine_log.txt','r') as fileReader:
    lines = fileReader.read ().splitlines ()
    last_line = lines[-1]
    fileReader.close()
with open('Vaccine_log.txt','w') as f:
    f.write(last_line)
    f.write('\n')

# To reset the logs ever 6 hours
