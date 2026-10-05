import json

# 1. nama fungsi
# 2. deskripsi fungsi
# 3. Parameter fungsi

# basic_template = {
#     'type': 'function',
#     'function': {
#         'name': 'describe_image',
#         'description': 'Describe the content of an image from a given URL.',
#         'parameters': {
#             'type': 'object',
#             'properties': {
#                 'image_url': {
#                     'type': 'string',
#                     'description': 'The URL of the image to be described'
#                 },
#             },
#             'required': ['image_url']
#         }
#     }
# }

internet_search_tool = {
    'type': 'function',
    'function': {
        'name': 'internet_search',
        'description': 'Search the internet for relevant information based on a query.',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'The search query to look up on the internet'
                },
            },
            'required': ['query']
        }
    }
}