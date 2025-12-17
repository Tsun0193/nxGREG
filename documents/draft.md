Make this update to the python file, in the first entites (the first heading level) 
"type": "display_conditions",

1. The content is including all the file content, which is not correct, this node shouldn't have any content
2. The property, under the heading there is a section of text like
the content:
**Target Screen:** Simple Contract (Paid Basic)  
**Main JSP:** `kihon.jsp`  
**Body JSP:** `body.jsp`  
**Primary Action:** `KihonInitAction`  
**Form Bean:** `yuusyou_keiyakuNewtmp_kihonForm`


The content should be break down and transform into  property for the first level entities "type": "display_conditions", and only for this entites
The rule for extraction can at each new line before the next heading the **key** should be key and the value should be value like this:
{
"Target Screen" : "Simple Contract (Paid Basic)"  
}