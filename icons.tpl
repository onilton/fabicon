%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)

<h3>Url:
{{url}}
</h3>
%#<p>The open items are as follows:</p>
%for candidateTag in candidateTags:
	<img src="{{candidateTag['url']}}" /> &nbsp;
%end
