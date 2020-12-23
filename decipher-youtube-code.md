# How to decipher the Youtube's signature?
Let's take a simple example.
## 1. first of all, we fetch the json strīng that contains our signature.
Here it is :
{"signatureCipher":"s=y%3Dj%3DgF73GjJvQ8Ht0ODXxjYwYqI7Rsy3wcTUWoPX6L4VescAiAOiMhyFo80Y%3DjNVS2-zpj7-MEFotUcqhOyEai0IdT0RNAhIARw8JQ0qOAAOAQ&sp=sig&url=https:\/\/r7---sn-8vq54voxpo-qxal\.googlevideo\.com/videoplayback%3Fexpire%3D1608756418%26ei%3DYljjX6b9Hv6AjuMP35aDoAk%26ip%3D1.38.246.2%26id%3Do-AI1Y35963EvKIOQ26-y2e6cQEkjr9sAg6kdVwqBdzvYw%26itag%3D251%26source%3Dyoutube%26requiressl%3Dyes%26mh%3Db1%26mm%3D31%252C26%26mn%3Dsn-8vq54voxpo-qxal%252Csn-cvh76ner%26ms%3Dau%252Conr%26mv%3Dm%26mvi%3D7%26pl%3D22%26initcwndbps%3D206250%26vprv%3D1%26mime%3Daudio%252Fwebm%26ns%3D762Ti-EupOTjlRqBunNwF30F%26gir%3Dyes%26clen%3D4090521%26dur%3D240.301%26lmt%3D1608020419873720%26mt%3D1608734446%26fvip%3D2%26keepalive%3Dyes%26c%3DWEB%26txp%3D5532434%26n%3DTyhRsSYSy2rhbeXX%26sparams%3Dexpire%252Cei%252Cip%252Cid%252Citag%252Csource%252Crequiressl%252Cvprv%252Cmime%252Cns%252Cgir%252Cclen%252Cdur%252Clmt%26lsparams%3Dmh%252Cmm%252Cmn%252Cms%252Cmv%252Cmvi%252Cpl%252Cinitcwndbps%26lsig%3DAG3C_xAwRAIgBiV-cXI3gPrZfC-zLu2Dl_5hCe6icfL4xkprGqYgjYQCIGpW4yeNmwgg-q-Wuur_SXgcnxrcapn6UQpXARWz6Ei1"}

## 2. Splitting it by '&', here's what we get:
### The signature
s=y%3Dj%3DgF73GjJvQ8Ht0ODXxjYwYqI7Rsy3wcTUWoPX6L4VescAiAOiMhyFo80Y%3DjNVS2-zpj7-MEFotUcqhOyEai0IdT0RNAhIARw8JQ0qOAAOAQ',   `we don't need the "s=", so will replace it with ''`
### Not of any use
'sp=sig',
### The Main URL
<p>'url=https://r7---sn-8vq54voxpo-qxal.googlevideo.com/videoplayback%3Fexpire%3D1608756418%26ei%3DYljjX6b9Hv6AjuMP35aDoAk%26ip%3D1.38.246.2%26id%3Do-AI1Y35963EvKIOQ26-y2e6cQEkjr9sAg6kdVwqBdzvYw%26itag%3D251%26source%3Dyoutube%26requiressl%3Dyes%26mh%3Db1%26mm%3D31%252C26%26mn%3Dsn-8vq54voxpo-qxal%252Csn-cvh76ner%26ms%3Dau%252Conr%26mv%3Dm%26mvi%3D7%26pl%3D22%26initcwndbps%3D206250%26vprv%3D1%26mime%3Daudio%252Fwebm%26ns%3D762Ti-EupOTjlRqBunNwF30F%26gir%3Dyes%26clen%3D4090521%26dur%3D240.301%26lmt%3D1608020419873720%26mt%3D1608734446%26fvip%3D2%26keepalive%3Dyes%26c%3DWEB%26txp%3D5532434%26n%3DTyhRsSYSy2rhbeXX%26sparams%3Dexpire%252Cei%252Cip%252Cid%252Citag%252Csource%252Crequiressl%252Cvprv%252Cmime%252Cns%252Cgir%252Cclen%252Cdur%252Clmt%26lsparams%3Dmh%252Cmm%252Cmn%252Cms%252Cmv%252Cmvi%252Cpl%252Cinitcwndbps%26lsig%3DAG3C_xAwRAIgBiV-cXI3gPrZfC-zLu2Dl_5hCe6icfL4xkprGqYgjYQCIGpW4yeNmwgg-q-Wuur_SXgcnxrcapn6UQpXARWz6Ei1'</p>

## What now? 

Youtube uses a simple approach to decipher(crack) the signature. It simply scrambles the signature(For ex : python ---> nyptoh). We have to place it back as needed i.e.(nyptoh --> python).

### But how do we decide which character where??
Actually, this work is done by the javascript of player. We simple need to get the part of javascript where this magic happens (Part because javascript is literally very big).
To find that part, we have some regex that gets that magical function for us.

## How to know in which part magic happens??
If we talk in javascript, there are two things. A variable and a function.
Youtube defines a variable and then calls a function again and again till processing is not done.
Here's that magical part:

#### The main function
```javascript
nw=function(a)
{
  a=a.split("");
  mw.p7(a,34);mw.qM(a,13);
  mw.UX(a,3);mw.p7(a,44);
  mw.qM(a,69);mw.UX(a,2);   
  mw.qM(a,58);mw.p7(a,24);
  mw.UX(a,1);
  return a.join("")
};
```
#### The main function's sub-function
```javascript
var mw=
{
    p7:function(a)
    {
      a.reverse()
    },
    UX:function(a,b)
    {
      a.splice(0,b)
    },
    qM:function(a,b)
    {
      var c=a[0];
      a[0]=a[b%a.length];
      a[b%a.length]=c
    }
};
  ```
  
 ### Ok, but how do we do that in python??
 We will use js2py library which converts the js to python equivalent. To grab the output from function, here's the simple line added to the function:
 ```javascript
var output = variable_name_from_above_js("The scrambled code");
 ```
 ### Here comes the final part
 We've the "descrambled code" now. We've to simple add it to url like this `url`+`&sig=`+`the descrambled signature`
 
