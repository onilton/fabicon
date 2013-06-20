<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Fabulous Favicon Crawler</title>
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le HTML5 shim, for IE6-8 support of HTML elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Le styles -->
    <link href="{{ get_url('static_root', filepath = 'css/bootstrap.css') }}" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
      }
    </style>
    
    <!--<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>-->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <!--<script src="js/iaabootstrap-modal.js"></script>-->
    <script src="{{ get_url('static_root', filepath = 'js/bootstrap.js') }}"></script>
    <script src="{{ get_url('static_root', filepath = 'js/jquery.pjax.js') }}"></script>
    <script type="text/javascript">
/*   $('a').pjax('#mainp').live('click', function(){
  $(this).showLoader()
    })*/

   $('button').live('click', function(){
  $(this).showLoader()
    });
    
    $(document).ready(function(){
 
	    $('#loadingDiv')
	    .hide()  // hide it initially
	    .ajaxStart(function() {
		$(this).show();
	    })
	    .ajaxStop(function() {
		$(this).hide();
	    })
	;
    if ("{{url}}" != ""){
	    $('#mainp').load("{{ get_url('icons') }}?url={{urlencoded}}");
		
   }
});

/*   $('form').pjax('').live('submit', function(){
  //$(this).showLoader()
  //$(this).showLoader()
  //$('#mainp').showLoader()
    })*/
    
    function generatePromos()
    {
    	var promoCodes = document.getElementById('promoCodes').value;
    	var appID = document.getElementById('appID').value;
    	
    	$.post('promos.php', { 'appID':appID, 'promoCodes':promoCodes },function(data) {

  			document.getElementById('alertBody').innerHTML = data;
    		
    		$('#modal-from-dom').modal({
  			keyboard: true,
  			backdrop: 'static',
  			show: true
			});
  			
		});

    }
    
    </script>

    <!-- Le fav and touch icons -->
    <link rel="shortcut icon" href="images/favicon.ico">
    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">
    <link rel="apple-touch-icon" sizes="72x72" href="images/apple-touch-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="114x114" href="images/apple-touch-icon-114x114.png">
    
    <script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-19767469-3']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
    
  </head>

  <body>

    <div class="topbar">
      <div class="fill">
        <div class="container">
          <a class="brand" href="#">fabicon</a>
          <ul class="nav">
            <li class="active"><a href="javascript:$('#aboutDialog').modal('show');">About</a></li>
            <li><a href="#">Blog</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="container">

      <!-- Main hero unit for a primary marketing message or call to action -->
      <div class="hero-unit">
        <h1>Fabulous Favicon Crawler</h1>
              	<p><b>Fabicon </b> (The <b>Fab</b>ulous Fav<b>icon</b> Crawler) helps you get better quality favicons, as large as we can find. Perfect for description of websites, but you could find other cool uses. <br/>Forget about those small ugly .ico files. </p>
        
%#        <p>
%#        <ul>
%#		<li>Enter your App ID</li>
%#        	<li>Enter your promo codes</li>
%#        	<li>Get back a URL that will automatically take you to the app store to redeem a promo code</li>
%#        </ul>
%#        </p>
        
	<h3>Type a website url:</h3>
		<form action="{{ get_url('index') }}" method="GET">
        <p>
		<input type="text" size="100" maxlength="100" name="url" placeholder="http://" />
     		%#<input type="text" id="appID" placeholder="App ID"/>
        </p>
        <p>
        	%#<textarea class="span10" placeholder="Paste promotional codes here" rows="10" id="promoCodes"></textarea>
        </p>
        %#<p><a class="btn primary large" href="javascript:generatePromos();">Create promo URL &raquo;</a></p>
	<p><button class="btn primary large" type="submit" >Get it!</button></p>
	</form>
	
	<div id='loadingDiv' style='display:none'><h4 ><img style="vertical-align:middle" src='img/spinner48.gif' /> <em>Loading...</em></h4></div>
	<div id='mainp'>
	<div class='loader' style='display:none'>Loading...<!--<img src='spin.gif'>--></div>
	
	%#include
	</div>
      	
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
      	
      </div>


<div class=content>
<!-- Rocket Droid -->
<!-- <section id="rocketdroid"> -->
<div class=page-header>
<h1>Examples <small>Some tested examples</small></h1>
</div>
<div class=row>
<div class=span10>
%#<h2>Description</h2>
%#<p>A Droid spin on the classic helicopter game. Basically an android flight simulator =) It's very easy and fun to play. Pressing the screen makes Rocket Droid fly up, and letting go allows him to fall. Try to keep him away from the canyon walls!</p>
%#<h5><strong>Release Date: </strong><em>January</em></h5>
<h4><strong>Globo: </strong><em> <a href="{{ get_url('index') }}?url=http%3A%2F%2Fglobo.com.br">http://globo.com.br</a></em></h4>
</div>
%#<div class=span4>
%#<h3>Download</h3>
%#<p>
%#<a href="https://market.android.com/details?id=com.oneapponemonth.rocketdroid">Google Market Place</a>
%#<br/>
%#<a href="http://www.amazon.com/gp/mas/dl/android?p=com.oneapponemonth.rocketdroid">Amazon Appstore</a>
%#</p>
%#</div>

</div>
<!-- </section> -->

%for site in exampleSites:
<div class=row>
<div class=span10>
<h4><strong>{{site['name']}}: </strong> <a href="{{ get_url('index') }}?url={{site['urlencoded']}}">{{site['url']}}</a></h4>
</div>
</div>
%end







%#END stuff --------------------------


%#      <footer>
%#       <p>&copy; Randall Brown 2011</p>
%#      </footer>
      
      <div id="modal-from-dom" class="modal hide fade" style="display: none; ">
            <div class="modal-header">
              <a href="#" class="close">×</a>
              <h3>Contact Me</h3>
            </div>
            <div class="modal-body" id="alertBody">
              <p></p>
            </div>
            <div class="modal-footer">
              <a href="javascript:$('#modal-from-dom').modal('hide');" class="btn primary">Thanks!</a>
            </div>
       </div>
       
       <div id="aboutDialog" class="modal hide fade" style="display: none; ">
            <div class="modal-header">
              <a href="#" class="close">×</a>
              <h3>About the Promo URL Generator</h3>
            </div>
            <div class="modal-body" id="alertBody">
              <p>Have you ever tried giving out iOS promo codes on Twitter? It sucks. <br/><br/>You post the code and the first person to see it claims it. Then everyone that sees it afterwards just fails. What if every person that clicked the link got their own promo code? That's what this does. <br/><br/>Click the link and they automatically get taken to the app store with their promo code. Pretty simple eh? </p>
            </div>
            <div class="modal-footer">
              <a href="javascript:$('#aboutDialog').modal('hide');" class="btn primary">Thanks!</a>
            </div>
       </div>
       
       <div id="contactDialog" class="modal hide fade" style="display: none; ">
            <div class="modal-header">
              <a href="#" class="close">×</a>
              <h3>Your Promo URL</h3>
            </div>
            <div class="modal-body" id="alertBody">
              <p><a href="https://twitter.com/intent/tweet?screen_name=randallwbrown" class="twitter-mention-button" data-size="large" data-related="randallwbrown">Tweet  @randallwbrown</a>
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script></p>
            </div>
            <div class="modal-footer">
              <a href="javascript:$('#contactDialog').modal('hide');" class="btn primary">Thanks!</a>
            </div>
       </div>
       

    </div> <!-- /container -->

  </body>
</html>

