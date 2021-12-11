# build_catalog.py
#
# By:           Josh Howe
# Created:      Sep 29, 2021
# Last updated: Sep 30, 2021
#
# A script to take a copy of Adam's "Master Class List" Google sheet format and turn it
# into a proper catalog for publishing to www.einsteinsworkshop.com/classes-top/class-catalog
#
# Usage:
#
#     python3 ./build_catalog.py {DATA}.tsv {CATALOG}.html
#
#  where DATA is the location and name of a TSV file of raw data from the Google sheet,
#     and CATALOG is the location where the new catalog html file will be saved.
#
# If the PRODUCTION environment variable is set, the output can be directly copy-pasted into the
# class-catalog article on Joomla. Otherwise, the output html will be standalone so it may be
# viewed directly in the browser without having to publish it first. The stylesheets and scripts
# Joomla uses behind-the-scenes will be added directly to the header, and a script will be
# injected that changes all of the URLs to point to the EW website instead of remaining
# relative paths.
#
# Note that the non-PRODUCTION config has only been tested and confirmed to work in Firefox.
#
import csv
import os
import sys
from urllib.parse import urlparse

category_order = [ 'coding', 'robotics', 'maker', 'game' ]

category_map = {
    'Coding':               'coding',
    'Robotics':             'robotics',
    'Making and Inventing': 'maker',
    'Game Learning':        'game'
}

section_heading_template = '''
<div id="{category}" class="section {category}">
<div class="section-title" style="background-color:{color};">{title}</div>
<div style="margin:10px;">
<div style="font-style:italic;">
<p style="margin: 0;">{description}</p>
</div>
<hr style="border: 2px solid {color}">'''

heading_parameters = {
    'coding': {
        'category': 'coding',
        'color': '#00adef',
        'title': 'Coding',
        'description': '''Coding at Einstein's Workshop is all about gaining confidence and solving problems. At the youngest ages students will play games with other students, learn how to program robots and begin internalizing the language of sequential code. Through the middle school years students will learn primarily though "Block Based Coding" - a computer based system of programming which uses preprogrammed "blocks" of code. Through Block Based Coding students can learn the language of code and make great programs without the nuances of punctuation and syntax which can so easily break their code. In high school students will begin programming in languages such as JAVA and Python to create small games, programs and even their own Minecraft Mods.'''
    },
    'robotics': {
        'category': 'robotics',
        'color': '#f6891e',
        'title': 'Robotics',
        'description': '''Robotics focuses on two core elements: Engineering and Programming. Students begin their robotics exploration using familiar tools like Lego. They learn about gears, belts, motors and movement and learn how to program their creations to perform simple tasks. As they grow students are encouraged to think outside the box and build unique solutions to solve problems.</p>
<p style="margin-top: 1vh; margin-bottom: 0;">Our program has access to First Lego League, a global robotics competition held every fall. And VEX IQ, another robotics system which we hold an in house competition for in the spring.'''
    },
    'maker': {
        'category': 'maker',
        'color': '#ed2a7b',
        'title': 'Making and Inventing',
        'description': '''The tools of the future are here and they are changing the way we build and design. At Einstein's Workshop students have access to a number of standard and modern tools and supplies. They will learn about physics, design, engineering, electronics, 2D Design, 3D Modeling and printing and much more. Over the course of our Making and Inventing curriculum students will learn confidence, hand skills and dexterity, problem solving and technical design skills.'''
    },
    'game': {
        'category': 'game',
        'color': '#3db056',
        'title': 'Game Learning',
        'description': '''Play is one of the greatest methods for teaching children. While all of our classes are fun, Game Learning takes it to the next level. From learning the social etiquette of playing games, to learning about electronics and the physics of orbital mechanics, to just plain fun, students will love their time in Game Learning classes.'''
    }
}

section_headings = {
    category: section_heading_template.format_map(parameters) \
        for category, parameters in heading_parameters.items()
}

frontmatter = '''<html>
<head>''' + (
  '''<title>Einstein's Workshop - STEM Classes for Kids - Class Catalog</title><link href="/templates/rt_callisto/favicon.ico" rel="shortcut icon" type="image/vnd.microsoft.icon"><link rel="stylesheet" href="/media/gantry5/assets/css/font-awesome.min.css" type="text/css"><link rel="stylesheet" href="/media/gantry5/engines/nucleus/css-compiled/nucleus.css" type="text/css"><link rel="stylesheet" href="/templates/rt_callisto/custom/css-compiled/callisto_20.css" type="text/css"><link rel="stylesheet" href="/media/gantry5/assets/css/bootstrap-gantry.css" type="text/css"><link rel="stylesheet" href="/media/gantry5/engines/nucleus/css-compiled/joomla.css" type="text/css"><link rel="stylesheet" href="/media/jui/css/icomoon.css" type="text/css"><link rel="stylesheet" href="/templates/rt_callisto/custom/css-compiled/callisto-joomla_20.css" type="text/css"><link rel="stylesheet" href="/templates/rt_callisto/custom/css-compiled/custom_20.css" type="text/css"><link rel="stylesheet" href="/templates/rt_callisto/custom/files/custom.css" type="text/css"><style type="text/css">#g-navigation .g-main-nav .g-toplevel > li:hover > .g-menu-item-container,#g-navigation .g-main-nav .g-toplevel > li.active > .g-menu-item-container{background: #24408e; color: #ffffff}#g-navigation .g-main-nav .g-dropdown{background: #008cef}#g-navigation .g-main-nav .g-dropdown li:hover > .g-menu-item-container{background: #24408e; color: #ffffff}.rokajaxsearch #roksearch_search_str{margin-bottom: 0}.inputbox.roksearch_search_str{color: rgb(0, 174, 239); height: 100%; } /* #g-showcase .g-container {width:100rem} */ #g-showcase .g-content {margin: 0; padding: 0} #g-mainfeature a { color: #00aeef; transition: all 0.2s ease 0s; background: transparent none repeat scroll 0 0; text-decoration: none; } #g-sidefeature a { color: #00aeef; transition: all 0.2s ease 0s; background: transparent none repeat scroll 0 0; text-decoration: none; } #g-sidefeature .moduletable .g-title { color: #24408e; font-size: 1.5rem; margin: 0 0 0.5rem; } #g-sidefeature .newsflash-title { margin: 0.75rem 0 0.5rem } #g-sidefeature p { margin: 0.3rem 0 } #g-footer {color: #ffffff} #g-footer .g-title, #g-footer .input-prepend {color: #00aeef} #g-footer li a {color: #ffffff} .g-social a {background: #00aeef none repeat scroll 0 0} #g-footer .input-small { color: rgb(0, 174, 239); height: 100%; } input[type="text"] {height: 100%} .input-prepend > .add-on, .input-append > .add-on { padding: 6px } </style> <script src="/media/jui/js/jquery.min.js" type="text/javascript"></script> <script src="/media/jui/js/jquery-noconflict.js" type="text/javascript"></script> <script src="/media/jui/js/jquery-migrate.min.js" type="text/javascript"></script> <script src="/media/system/js/caption.js" type="text/javascript"></script> <script src="/media/jui/js/bootstrap.min.js" type="text/javascript"></script> <script type="text/javascript"> jQuery(document).ready(function(){jQuery.contentIdPlugin.contentIdValue('page-item')}); jQuery(window).on('load',  function() { new JCaption('img.caption'); }); (function($){$(window).ready(function(){$(".wf-media-input").removeAttr("readonly");})})(jQuery); jQuery(document).ready(function(){jQuery.contentIdPlugin.contentIdValue('page-item')}); </script> <style type="text/css">#mc_embed_signup input.mce_inline_error { border-color:#6B0505; } #mc_embed_signup div.mce_inline_error { margin: 0 0 1em 0; padding: 5px 10px; background-color:#6B0505; font-weight: bold; z-index: 1; color:#fff; }</style><style type="text/css">.c1-ui-state-hover {background-color:yellow !important; padding:5px !important }</style>''' \
    if 'PRODUCTION' not in os.environ else ''
) + '''
<style>
.title            { text-align: left; width: 100%; }
.category-heading { border: solid 4px white; color: #ffffff; font-size: 110%; text-align: center; }
.section-title    { color: white; font-size: 150%; font-weight: bold; letter-spacing: 1px; width: 100%; }
.img2             { border-radius: 5px; float: right; max-height: 150px; }
.section          { border-left-width: 20px; border-radius: 5px; border: 3px solid; margin: 5px 0px; }
#coding           { border-color: #00adef; }
#robotics         { border-color: #f6891e; }
#maker            { border-color: #ed2a7b; }
#game             { border-color: #3db056; }
#summer           { margin: 5px 0px; }
.entry            { margin-top: 10px; }
</style>
</head>
<body>
<p>Welcome to the Einstein's Workshop school year catalog. Here you will find brief descriptions of the classes we are running this 2021-22 school year.</p>
<p>Our classes are divided into four categories. The categories exist to assist you in understanding what the core concept of the class is. Most of our classes are inherently interdisciplinary and use many tools. For more information please do not hesitate to contact us!</p>
<div class="w3-row">'''

category_headings_template = '''
<div class="w3-quarter w3-container category-heading" style="background-color:{color}">{title}</div>'''

for category in category_order:
    frontmatter += category_headings_template.format_map(heading_parameters[category])

frontmatter += '''
</div>'''

endmatter = '''
</body>
<script>
function expando(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else {
        x.className = x.className.replace(" w3-show", "");
    }
}''' + ('''

(function () {
let regexStr = '^(' + window.location.origin +')?';
let regex = new RegExp(regexStr);
let imgs = document.getElementsByTagName('img');
for (let i = 0; i < imgs.length; i++) {
    imgs[i].src = imgs[i].src.replace(regex, 'http://www.einsteinsworkshop.com');
}

let links = document.getElementsByTagName('link');
for (let i = 0; i < links.length; i++) {
    links[i].href = links[i].href.replace(regex, 'http://www.einsteinsworkshop.com');
}

let scripts = document.getElementsByTagName('script');
for (let i = 0; i < scripts.length; i++) {
    if (scripts[i].src) {
        scripts[i].src = scripts[i].src.replace(regex, 'http://www.einsteinsworkshop.com');
    }
}

})()''' if 'PRODUCTION' not in os.environ else ''
) + '''
</script>
</html>'''

def build_catalog(tsv_sourcefile, html_destination, prod=False):
    with open(html_destination, 'w') as catalog:
        catalog.write(frontmatter)

        classes_by_category = {}
        with open(tsv_sourcefile, 'r', newline='') as sourcedata:
            reader = csv.reader(sourcedata, delimiter='\t')

            header_line = True
            for row in reader:
                if header_line:
                    header_line = False
                    continue
                category_long_name, *rest = row
                category = category_map[category_long_name]
                if row[-1] == 'Yes':
                    if category not in classes_by_category:
                        classes_by_category[category] = []
                    classes_by_category[category].append(rest)

        for category in category_order:
            catalog.write(section_headings[category])

            for i, class_info in enumerate(classes_by_category[category]):
                title, description, picture, _min_grade, _max_grade, _camp_or_class, _season, \
                        web_anchor, *_rest = class_info
                catalog_expand = f'{category}{i}'
                catalog.write(f'''

<div id="{web_anchor}" class="entry">
<button onclick="expando('{catalog_expand}')" class="w3-btn title">
<strong style="font-size:115%;">{title}</strong>
</button>
<div id="{catalog_expand}" class="w3-container w3-hide">
<div class="w3-row">
<div class="w3-threequarter description">
<p>{description}</p>
</div>''' + (f'''
<div class="w3-quarter">
<img class="img2" alt="" src="{urlparse(picture).path}">
</div>
''' if len(picture) > 0 else '') + '''
</div>
<hr />
</div>
</div>''')

            catalog.write('''
</div>
</div>
''')

        catalog.write(endmatter)

if __name__ == '__main__':
    build_catalog(sys.argv[1], sys.argv[2])
