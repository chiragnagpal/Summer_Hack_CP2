
# coding: utf-8

# In[1]:

def txt_dict(filename):
     
    import ujson
    #test loading the file, printing sample contents
    with open(filename,'r') as fp:
        temp = ujson.load(fp);
    #print '# elements: ', len(temp1)
    #print 'sample of contents:'
    #print repr(temp1[1]).decode("unicode-escape")
    return temp


# In[2]:

def collapse_data(data):
    
    users = {}
    
    
    for item in data:
        
        user = users.get(item['userName'], None)
        
        if user != None:
       
            user['groupName'].add(item['groupName'])    
            if item['imageName'] is not None:
         
        
                user['image'].add( (item['imageName'],item['imageHeight'],item['imageWidth'],item['imageType'],item['imageSize']))
    
            fieldName = item.get('userProfileFieldName', None)
            
            if fieldName is not None:
            
                user[fieldName] = item['userProfileFieldValue']
    
    
        else:
        
            user = item['userName']
        
            users[user] = {}
        
            users[user]['groupName'] = set([item['groupName']])
            
            users[user]['registrationTime']= item['registrationTime']
            
            if item['imageName'] is not None:
            
            
                users[user]['image']= set( [(item['imageName'],item['imageHeight'],item['imageWidth'],item['imageType'],item['imageSize'])] ) 
                
                
            else:
                
                users[user]['image'] =set([])
        
    return users


# In[3]:

def usr_bow(posts):
    
    posts_bow = {}
    
    for post in posts:
    
        if posts_bow.get(post['userName'], None) == None:
            
            posts_bow[post['userName']] = {}
            
            posts_bow[post['userName']]['body'] = [post['postBody']  ]
            
            posts_bow[post['userName']]['subject'] = [post['postSubject']  ]
            
            posts_bow[post['userName']]['title'] = [post['threadTitle']  ]
            
            posts_bow[post['userName']]['postTime'] = [post['postTime']]
        
         
        else:
            
            posts_bow[post['userName']]['body'] = posts_bow[post['userName']]['body']  + [post['postBody']]
            
            posts_bow[post['userName']]['subject'] = posts_bow[post['userName']]['subject'] +[post['postSubject']  ]

            posts_bow[post['userName']]['title'] = posts_bow[post['userName']]['title'] + [post['threadTitle']  ]
            
            posts_bow[post['userName']]['postTime'] = posts_bow[post['userName']]['postTime'] + [post['postTime']]
            
    return posts_bow


# In[ ]:

def check_exist(usrA, usrB, usrsA, usrsB, postsA, postsB, ):
    
    
    if usrA not in usrsA.keys():
        
        return 0
    
    if usrB not in usrsB.keys():
        
        return 0
    
    if usrA not in postsA.keys():
        
        return 0
    
    if usrB not in postsB.keys():
        
        return 0
    
    return 1


# In[4]:


def gen_pos_pairs(filename,  postsA, postsB, usrsA, usrsB):

    import ujson
    import ftfy

    with open(filename, 'rb') as f:
        data = f.readlines()

    data = map(lambda x: x.rstrip(), data)

    # convert to array of JSON objects
    data_json_str = "[" + ','.join(data) + "]"

    # load it
    data_gt = ujson.loads(data_json_str)

    X = []
    
    for pair in data_gt:
        
        if pair['class'] == 1:
            
            usr1 = pair['site_a']
            
            usr2 = pair['site_b']
            
           # if not check_exist(usr1, usr2, usrsA, usrsB, postsA, postsB):
                
            #    continue
            
            
            if usr2 == u'Ghost\u2122':
                
                usr2 = "GhostTM"
                
            if usr2 == u'nicklan&lt;b&gt;&lt;/b&gt;':
                
                usr2 = u'nicklan<b></b>'
            
            X.append(featurise(usr1, usr2,  postsA, postsB, usrsA, usrsB))
            
            
    return X


# In[5]:

def gen_neg_pairs(filename, postsA, postsB, usrsA, usrsB):
    
    import ujson
    import ftfy
    
    import random

    with open(filename, 'rb') as f:
        data = f.readlines()

    data = map(lambda x: x.rstrip(), data)

    # convert to array of JSON objects
    data_json_str = "[" + ','.join(data) + "]"

    # load it
    data_gt = ujson.loads(data_json_str)

    X = []
    
    pos = []
    
    for pair in data_gt:
        
        if pair['class'] == 1:
            
            pos.append((pair['site_a'],pair['site_b']))
            
    for i in range(len(data_gt)):
        
        
        usr1 = random.choice(usrsA.keys())
        
        usr2 = random.choice(usrsB.keys())
        
        if (usr1, usr2) not in pos:
        
        
            X.append(featurise(usr1, usr2,  postsA, postsB, usrsA, usrsB))

            
    return X


# In[6]:

def text_to_vector(text):
    
    from collections import Counter
    return Counter(text)


# In[7]:

def get_cosine(vec1, vec2):
    
    import math
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def replace_punct(st):
    
    import string
    import re

    
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    out = regex.sub(' ', st)
    
    return out

def indi_scores(l1, l2):
    
    import numpy as np
    
    l1_t = []
    
    l2_t = []
    
    
    for item in l1:
        
        l1_t.append(set(replace_punct(item).lower().split()))
    
    for item in l2:
        
        l2_t.append(set(replace_punct(item).lower().split()))

    l1 = l1_t
    
    l2 = l2_t
        
    
    scores_jac = []
    
    scores_cs = []
    
    
    for item in l1:
        
        for item2 in l2:
            
            if len(item|item2) == 0:
                scores_jac.append(0)
            else:
                scores_jac.append(  float(len(item&item2))/float((len(item|item2))) )   
    
            vec1 = text_to_vector(item)
            vec2 = text_to_vector(item2)
    
            scores_cs.append(get_cosine(vec1, vec2))
    
    cs_feats = [ min(scores_cs), max(scores_cs), np.mean(scores_cs)     ]
    
    
    
    jac_feats = [ min(scores_jac), max(scores_jac), np.mean(scores_cs)]
    
    return cs_feats + jac_feats 


# In[9]:




def overall_scores(l1, l2):
    
    
    vec = []
    
    item = set()
    
    item2 = set()
    
    for it in l1:
        
        item |= set(replace_punct(it).lower().split())
        
    for it in l2:
    
        item2 |= set(replace_punct(it).lower().split())
        
    
    
    if len(item|item2) == 0:
            
        vec.append(0)
        
    else:
        vec.append(  float(len(item&item2))/float((len(item|item2))) )   

    vec1 = text_to_vector(item)
    vec2 = text_to_vector(item2)
    
    vec.append(get_cosine(vec1, vec2))
        
    return vec

def post_freq(time):
    
    mn = min(time)
    
    mx = max(time)
    
    return float(mx-mn)/len(time)

def post_std(time):
    
    import numpy as np
    
    return np.std(time)

def post_mn(time):
    
    import numpy as np
    
    return np.mean(time)

def post_time(usr1, usr2, postsA, postsB, usrsA, usrsB):
    
    vector = []
    
    time1 = []
    
    time2 = []
    
    for post in postsA[usr1]['postTime']:
        
        time1.append(int(post))
        
    for post in postsB[usr2]['postTime']:
        
        time2.append(int(post))
        
    vector.append( abs(post_std(time1) - post_std(time2 ) ) )
                      
    vector.append(abs(post_freq(time1) - post_freq(time2) ))
                  
    vector.append(abs( post_mn(time1) - post_mn(time2)  )) 
                  
    return vector
    
    

    
        
def featurise( usr1, usr2, postsA, postsB, usrsA, usrsB  ):
    
    import editdistance
    
    
    vector = []
    
    
    #feature1 : editDist between usernames
    
    
    username1 = usr1
    
    username2 = usr2
    
    ft1 = editdistance.eval(usr1, usr2)

    vector.append(int(ft1))
    
    
    #feature2 : editDist between lowercase usernames
    
    ft2 = editdistance.eval(usr1.lower(), usr2.lower())
    
    vector.append(int(ft2))
    
    
    if len(usr1) > len(usr2):
            
            norm = len(usr1)
    
    else:
        
            norm = len(usr2)
    
    ft1 = float(ft1)/norm

    ft2 = float(ft2)/norm

    vector.append(ft1)

    vector.append(ft2)
    
    #feature3 : timediff between user     
    
    ft3 =  abs(usrsA[usr1]['registrationTime'] - usrsB[usr2]['registrationTime'])
    
    vector.append(int(ft3))
    
    #feature4: TimeZone
    
    if usrsA[usr1]['Time Zone'] == usrsB[usr2]['Time Zone']:
    
        ft4 = 1
        
    else:
        
        ft4 = 0
    
    vector.append(ft4)
  
    #text Features
    
    #feature 5: Textual, Individual, overall
    
    if (postsA.get(usr1, None) != None) and (postsB.get(usr2, None) != None):
    
    
        ft5 = indi_scores(postsA[usr1]['body'],postsB[usr2]['body'])

        ft5 = ft5 + indi_scores(postsA[usr1]['subject'],postsB[usr2]['subject'])

        ft5 = ft5 + indi_scores(postsA[usr1]['title'],postsB[usr2]['title'])

        vector += ft5    
        
        
                
        ft6 = overall_scores(postsA[usr1]['body'],postsB[usr2]['body'])

        ft6 = ft6 + overall_scores(postsA[usr1]['subject'],postsB[usr2]['subject'])

        ft6 = ft6 + overall_scores(postsA[usr1]['title'],postsB[usr2]['title'])
                 

        vector += ft6 
                
        vector += post_time( usr1, usr2, postsA, postsB, usrsA, usrsB )         
                  
    else:
        
        vector += [-1 for i in range(18)]
        
        vector +=[-1 for i in range(6)]
                  
        vector +=[-1 for i in range(3)]
    
    #feature7: Group Affliations
    
    groups1 = usrsA[usr1]['groupName']
    
    groups2 = usrsB[usr2]['groupName']
    
    n = 0
    
    for item in groups1:
        
        for item2 in groups2:

            if item[:3].lower() == item2[:3].lower():
                
                n+=1
                
    ft7 = n
    
    vector.append(ft7)

    
    #feature8: Signatures
    
    sig1 = usrsA[usr1].get("Signature", None)
    
    sig2 = usrsB[usr2].get("Signature", None)
    
    ft8 = -1
    
    ft9 = -1
    
    if (sig1!=None) and (sig2!=None):
        
        sig1 = replace_punct(sig1).lower().split()
        
        sig2 = replace_punct(sig2).lower().split()
        
        ssig1 = set(sig1)
        
        ssig2 = set(sig2)
        
        ft8 = float(len(ssig1&ssig2))/float((len(ssig1|ssig2)))
        
        sig1 = text_to_vector(sig1)

        sig2 = text_to_vector(sig2)
        
        ft9 = get_cosine(sig1, sig2)
    
    vector.append(ft8)
    
    vector.append(ft9)
    
    
    
        
    return vector


# In[ ]:

def check_feat(key, d):
    
    for item in d:
        
        if key not in d[item].keys():
            return "Not There", item
    
    
    return "there in every element! :)"

