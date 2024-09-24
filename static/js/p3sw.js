function hide_edit_div() {
  var d = document.getElementById("editor_d");
  d.style.display = "none";
}

function toggle_edit_div() {
  var d = document.getElementById("editor_d");
  var b = document.getElementById("edit_btn");
  if (d.style.display === "block") {
    //console.log("hide editor div");
    hide_edit_div();
    // change the Edit btn to make it clear
    b.style.color = "#b2b22b";
    b.style.backgroundColor = "#ffffff";
    //b.style.backgroundColor = "#04AA6D";
  } else {
    d.style.display = "block";
    b.style.color = "#04AA6D";
    b.style.backgroundColor = "#b2b22b";
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
  }
}

function check_submit(){
    //localStorage.setItem('lastSubmitUrl', document.URL.split("?")[0]);
    localStorage.setItem('lastSubmitUrl', window.location);
    // check that this isn't an F5 or Ctrl+r
    // by inspecting localStorage.getItem('lastSubmitUrl');
    // which is cleared by a proper page load but not
    // when the form is submitted
    var has_submit = localStorage.getItem('resubmitcheck');
    var rsc = document.getElementById("resubmitcheck").value;
    localStorage.setItem('resubmitcheck', rsc);
    if (typeof has_submit === 'undefined' || has_submit != rsc){
        console.log("totally Valid: rsc " + rsc + "; has_submit: " + has_submit);
        //e.preventDefault();    //DEBUG: stop form from submitting
        return true;
    }else{
        alert("You already submitted that; Reload the page.");
        console.log("Prevent resubmit ACTIVATED¬!");
        e.preventDefault();    //stop form from submitting
        return false;
    }
}

function clear_submit_token(){
    localStorage.removeItem('lastSubmitUrl');
}

function cmp_submit(){
    var last_submit =  localStorage.getItem('lastSubmitUrl');
    // var cur_href = document.URL.split("?")[0];
    var cur_href = window.location.href;
    if (typeof last_submit !== 'undefined' || last_submit === window.location.href){
        return true
    }
    return false
}

/* prevent F5 overwriting */
/* RDFs:src="https://stackoverflow.com/a/66607233/1153645" */

document.addEventListener('keydown', (e) => {
    e = e || window.event;
    if(e.keyCode == 116){ // F5 key
        if(cmp_submit()){
          //window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
          window.location.href = document.URL;
          e.preventDefault();
          return true;
        }
    } else if(e.keyCode == 82){ // R button
        if (e.ctrlKey){
           event.returnValue = false;
           event.keyCode = 0;
            if(cmp_submit()){
              e.preventDefault();
              window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
              return true;
            }
        }
    }
});

function makeid(length) {
   /* RDFa:src="http://stackoverflow.com/questions/1349404/ddg#1349426" */
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

function set_messageId(){
  var d = document.getElementById("editor_t");
  if (typeof d === 'undefined'){
    console.log("unable to set editor_t messageId");
  }else if(d){
   var rnd_str = makeid(5);
    //console.log("editor_t messageId:" + typeof(d) + "; rnd_str: " + rnd_str);
    d.insertAdjacentHTML('afterend', '<input id="resubmitcheck" type="hidden" value="' + rnd_str + '" name="resubmitcheck" />');
  //}else{
  //  console.log("ELSE editor_t messageId:" + d.value + "; rnd_str: " + rnd_str);
  }
}

document.addEventListener("DOMContentLoaded", function() {
  set_messageId();
  hide_edit_div();
  document.querySelector("#edit_btn").addEventListener("click", function(){
    toggle_edit_div();
  });
  document.querySelector("#editor_f").addEventListener("submit", function(){
    check_submit();
  });
});

function setSearchAction(){
    var s_value = document.getElementById("search_i").value;
    document.getElementById("search_f").action = "/wiki/search/" + s_value;
}
