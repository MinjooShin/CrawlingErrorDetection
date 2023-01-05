from configparser import ConfigParser

config = ConfigParser()

config['DB'] = {
    'MONGO_URI' : 'mongodb://localhost:27017',
    'MONGO_DB' : 'KUBIC'
}

config['VARS'] = {
    'VAR1' : 'post_title',
    'VAR2' : 'post_body',
    'VAR3' : 'post_writer',
    'VAR4' : 'post_date',
    'VAR5' : 'published_institution',
    'VAR6' : 'published_institution_url',
    'VAR7' : 'top_category',
    'VAR8' : 'original_url',
    'VAR9' : 'file_name',
    'VAR10' : 'file_download_url',
    'VAR11' : 'file_id_in_fsfiles',
    'VAR12' : 'file_extracted_content',
    'var13' : 'hash_key',
    'var14' : 'timestamp'
}

config['LOCAL'] = {
    'PATH_SPIDER' : '/Users/minjooshin/kubicPJ2/CrawlingErrorDetection/CrawlingErrorDetection/spiders'
}

config['SERVER'] = {
    'PATH_SPIDER' : '/home/minjoo/Project/CrawlingErrorDetection/CrawlingErrorDetection/spiders'
}

with open('./config.cnf', 'w') as f:
    config.write(f)