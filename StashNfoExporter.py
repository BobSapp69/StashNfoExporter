import os
import requests
import lxml.etree as etree
import datetime
import config
import log

graphqlUrl=config.graphql_url
headers = {
    'Content-Type': 'application/json',
    'ApiKey': f'{config.api_key}',
    }

def stashSceneInfo(sceneId):
    json={
    "operationName": "FindScene",
    "variables": {
        "id": sceneId
    },
    "query": "query FindScene($id: ID!, $checksum: String) { findScene(id: $id, checksum: $checksum) { ...SceneData __typename } } fragment SceneData on Scene { id title code details director urls date rating100 o_counter organized interactive interactive_speed captions { language_code caption_type __typename } created_at updated_at resume_time last_played_at play_duration play_count files { ...VideoFileData __typename } paths { screenshot preview stream webp vtt sprite funscript interactive_heatmap caption __typename } scene_markers { ...SceneMarkerData __typename } galleries { ...SlimGalleryData __typename } studio { ...SlimStudioData __typename } movies { movie { ...MovieData __typename } scene_index __typename } tags { ...SlimTagData __typename } performers { ...PerformerData __typename } stash_ids { endpoint stash_id __typename } sceneStreams { url mime_type label __typename } __typename } fragment VideoFileData on VideoFile { id path size mod_time duration video_codec audio_codec width height frame_rate bit_rate fingerprints { type value __typename } __typename } fragment SceneMarkerData on SceneMarker { id title seconds stream preview screenshot scene { id __typename } primary_tag { id name __typename } tags { id name __typename } __typename } fragment SlimGalleryData on Gallery { id title code date urls details photographer rating100 organized files { ...GalleryFileData __typename } folder { ...FolderData __typename } image_count cover { id files { ...ImageFileData __typename } paths { thumbnail __typename } __typename } chapters { id title image_index __typename } studio { id name image_path __typename } tags { id name __typename } performers { id name gender favorite image_path __typename } scenes { ...SlimSceneData __typename } __typename } fragment GalleryFileData on GalleryFile { id path size mod_time fingerprints { type value __typename } __typename } fragment FolderData on Folder { id path __typename } fragment ImageFileData on ImageFile { id path size mod_time width height fingerprints { type value __typename } __typename } fragment SlimSceneData on Scene { id title code details director urls date rating100 o_counter organized interactive interactive_speed resume_time play_duration play_count files { ...VideoFileData __typename } paths { screenshot preview stream webp vtt sprite funscript interactive_heatmap caption __typename } scene_markers { id title seconds primary_tag { id name __typename } __typename } galleries { id files { path __typename } folder { path __typename } title __typename } studio { id name image_path __typename } movies { movie { id name front_image_path __typename } scene_index __typename } tags { id name __typename } performers { id name gender favorite image_path __typename } stash_ids { endpoint stash_id __typename } __typename } fragment SlimStudioData on Studio { id name image_path stash_ids { endpoint stash_id __typename } parent_studio { id __typename } details rating100 aliases __typename } fragment MovieData on Movie { id name aliases duration date rating100 director studio { ...SlimStudioData __typename } synopsis url front_image_path back_image_path scene_count scenes { id title __typename } __typename } fragment SlimTagData on Tag { id name aliases image_path parent_count child_count __typename } fragment PerformerData on Performer { id name disambiguation url gender twitter instagram birthdate ethnicity country eye_color height_cm measurements fake_tits penis_length circumcised career_length tattoos piercings alias_list favorite ignore_auto_tag image_path scene_count image_count gallery_count movie_count performer_count o_counter tags { ...SlimTagData __typename } stash_ids { stash_id endpoint __typename } rating100 details death_date hair_color weight __typename }"
    }
    
    response = requests.post(graphqlUrl, json=json, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        performer_name=[]
        performer_image=[]
        scene_tags=[]
        performer_gender=[]
        stash_ids=[]

        for tags in json_response['data']['findScene']['tags']:
            scene_tags.append(tags['name'])

        for performer in json_response['data']['findScene']['performers']:
            performer_name.append(performer['name'])
            performer_image.append(performer['image_path'])
            performer_gender.append(performer['gender'])
        
        for ids in json_response['data']['findScene']['stash_ids']:
            stash_ids.append(ids['stash_id'])


        title=json_response['data']['findScene']['title']
        id=json_response['data']['findScene']['id']
        details=json_response['data']['findScene']['details']
        
        if (json_response['data']['findScene']['studio']) is not None:
            studio=json_response['data']['findScene']['studio']['name']
        else:
            studio=""
            

        director=json_response['data']['findScene']['director']
        rating=json_response['data']['findScene']['rating100']
        date_created=json_response['data']['findScene']['created_at']
        date_released=json_response['data']['findScene']['date']
        if date_released is not None:
            year_released=datetime.datetime.strptime(date_released, "%Y-%m-%d").year
        else:
            year_released=""
        play_count=json_response['data']['findScene']['play_count']
        codec=json_response['data']['findScene']['files'][0]['video_codec']
        width=json_response['data']['findScene']['files'][0]['width']
        height=json_response['data']['findScene']['files'][0]['height']
        durationinseconds=json_response['data']['findScene']['files'][0]['duration']
        audio_codec=json_response['data']['findScene']['files'][0]['audio_codec']
        thumb_poster=json_response['data']['findScene']['paths']['screenshot']
        file_path=json_response['data']['findScene']['files'][0]['path']

        return title,id,play_count,date_created,date_released,rating,details,studio,director,performer_name,performer_image,scene_tags,codec,width,height,durationinseconds,audio_codec,thumb_poster,performer_gender,year_released,file_path,stash_ids
    else:
        print(f"Error: {response.status_code} - {response.text}")


def generateNFO(data):

    title,id,play_count,date_created,date_released,rating,details,studio,director,performer_name,performer_image,scene_tags,codec,width,height,durationinseconds,audio_codec,thumb_poster,performer_gender,year_released,file_path,stash_ids=data

    root = etree.Element("movie")
    
    title_element = etree.SubElement(root, "title")
    title_element.text = title

    originaltitle_element = etree.SubElement(root, "originaltitle")
    originaltitle_element.text = title

    id_element = etree.SubElement(root,"uniqueid")
    id_element.text = id

    for ids in stash_ids:
        stash_id_element = etree.SubElement(root,"uniqueid",type="stashdb")
        stash_id_element.text = str(ids)

    mpaa_element = etree.SubElement(root,"mpaa")
    mpaa_element.text = "XXX"

    playcount_element = etree.SubElement(root,"playcount")
    playcount_element.text = str(play_count)

    dateadded_element = etree.SubElement(root,"dateadded")
    dateadded_element.text = date_created

    premiered_element = etree.SubElement(root,"premiered")
    premiered_element.text = date_released

    year_element =  etree.SubElement(root,"year")
    year_element.text = str(year_released)

 
    userrating_element = etree.SubElement(root,"userrating")
    userrating_element.text = rating

    plot_element = etree.SubElement(root,"plot")
    plot_element.text = details

    studio_element = etree.SubElement(root,"studio")
    studio_element.text = studio

    director_element = etree.SubElement(root,"director")
    director_element.text = director

    thumb_poster_element = etree.SubElement(root,"thumb",attrib={"aspect":"poster"})
    thumb_poster_element.text = thumb_poster

    for i in range(len(performer_name)):
        actor_element  = etree.SubElement(root,"actor")
        name_element = etree.SubElement(actor_element,"name")
        gender_element = etree.SubElement(actor_element,"gender")
        gender_element.text = performer_gender[i]
        role_element = etree.SubElement(actor_element,"role")
        order_element = etree.SubElement(actor_element,"order")
        order_element.text = str(i)
        name_element.text = performer_name[i]
        image_element = etree.SubElement(actor_element,"thumb",attrib={"aspect":"poster"})
        image_element.text = performer_image[i]
       
    genre_element = etree.SubElement(root,"genre")

    for tags in scene_tags:
        tag_element = etree.SubElement(root,"tag")
        tag_element.text = tags

    fileinfo_element = etree.SubElement(root,"fileinfo")
    streamdetails_element = etree.SubElement(fileinfo_element,"streamdetails")
    video_element = etree.SubElement(streamdetails_element,"video")
    codec_element = etree.SubElement(video_element,"codec")
    codec_element.text = codec
    width_element = etree.SubElement(video_element,"width")
    width_element.text = str(width)
    height_element = etree.SubElement(video_element,"height")
    height_element.text = str(height)
    durationinseconds_element = etree.SubElement(video_element,"durationinseconds")
    durationinseconds_element.text = str(durationinseconds)
    audio_element = etree.SubElement(streamdetails_element,"audio")
    audio_codec_element = etree.SubElement(audio_element,"codec")
    audio_codec_element.text = audio_codec

    original_filename_element = etree.SubElement(root,"original_filename")
    original_filename_element.text = os.path.basename(file_path)
    
    
    base_dir=os.path.dirname(file_path)

    xml_string = etree.tostring(root, pretty_print=True,xml_declaration=True,encoding="utf-8")
    with open(f"{base_dir}/movie.nfo", "wb") as f:
        f.write(xml_string)
        log.info(f"Added nfo for {title} [Id -> {id}] [File -> {file_path}]")

json={
  "operationName": "FindScenes",
  "variables": {
    "filter": {
      "q": "",
      "page": 1,
      "per_page": 40,
      "direction": "DESC"
    },
    "scene_filter": {
      "movies": {
        "value": [],
        "modifier": "IS_NULL"
      },
      "organized": config.organized
    }
  },
  "query": "query FindScenes($filter: FindFilterType, $scene_filter: SceneFilterType, $scene_ids: [Int!]) {\n  findScenes(filter: $filter, scene_filter: $scene_filter, scene_ids: $scene_ids) {\n    count\n    filesize\n    duration\n    scenes {\n      ...SlimSceneData\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SlimSceneData on Scene {\n  id\n  title\n  code\n  details\n  director\n  urls\n  date\n  rating100\n  o_counter\n  organized\n  interactive\n  interactive_speed\n  resume_time\n  play_duration\n  play_count\n  files {\n    ...VideoFileData\n    __typename\n  }\n  paths {\n    screenshot\n    preview\n    stream\n    webp\n    vtt\n    sprite\n    funscript\n    interactive_heatmap\n    caption\n    __typename\n  }\n  scene_markers {\n    id\n    title\n    seconds\n    primary_tag {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  galleries {\n    id\n    files {\n      path\n      __typename\n    }\n    folder {\n      path\n      __typename\n    }\n    title\n    __typename\n  }\n  studio {\n    id\n    name\n    image_path\n    __typename\n  }\n  movies {\n    movie {\n      id\n      name\n      front_image_path\n      __typename\n    }\n    scene_index\n    __typename\n  }\n  tags {\n    id\n    name\n    __typename\n  }\n  performers {\n    id\n    name\n    gender\n    favorite\n    image_path\n    __typename\n  }\n  stash_ids {\n    endpoint\n    stash_id\n    __typename\n  }\n  __typename\n}\n\nfragment VideoFileData on VideoFile {\n  id\n  path\n  size\n  mod_time\n  duration\n  video_codec\n  audio_codec\n  width\n  height\n  frame_rate\n  bit_rate\n  fingerprints {\n    type\n    value\n    __typename\n  }\n  __typename\n}"
}
response = requests.post(graphqlUrl, json=json, headers=headers)
if response.status_code == 200:
    json_response = response.json()
    for ids in json_response['data']['findScenes']['scenes']:
        generateNFO(data=stashSceneInfo(ids['id'])) 
else:
    print(f"Error: {response.status_code} - {response.text}")