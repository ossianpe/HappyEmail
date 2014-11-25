#Options for Google Custom Search API
#https://developers.google.com/custom-search/json-api/v1/reference/cse/list
#And a little more here https://developers.google.com/custom-search/docs/xml_results

#Left unspecified results could be webpages
SEARCH_TYPE = 'image'

#Image Type. Acceptable values are: 
#  "clipart": clipart
#  "face": face
#  "lineart": lineart
#  "news": news
#  "photo": photo
IMAGE_TYPE = 'photo'

#File type. Acceptable values are:
#  "bmp"
#  "gif"
#  "png"
#  "jpg"
#  "svg"
FILE_TYPE = 'png'

#Search safety level. Acceptable values are:
#  "high": Enables highest level of SafeSearch filtering.
#  "medium": Enables moderate SafeSearch filtering.
#  "off": Disables SafeSearch filtering. (default)
SAFE_SEARCH = 'high'