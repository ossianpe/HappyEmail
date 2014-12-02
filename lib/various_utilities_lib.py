import os
import urllib2

class VariousUtilities:
    def check_connection(self, test_url):
        try:
            response = urllib2.urlopen(test_url, timeout=1)
            print "Connected to \"" + test_url + " successfully."
        except urllib2.URLError as err:
            print "No connection to " + "\"" + test_url + "\". Hmm..."
            exit()
    
    def open_subdirectory(self, relative_location, subdir, file_name):
        script_dir = os.path.dirname(relative_location) #<-- absolute dir the script is in
        rel_path = subdir + file_name
        return os.path.join(script_dir, rel_path)
    
    def check_file(self, file_name_and_location):
        if os.path.isfile(file_name_and_location):
            return "true"
        else:
            print "Error: Missing Database"
            time.sleep(1)
            return "false"