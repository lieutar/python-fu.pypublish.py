(function(){

   /*
    * pypublish.js
    * -----------------------------------------------------
    * pypublish.py を SendTo から使うためのラッパスクリプト
    *
    * このスクリプトのショートカットをSendToフォルダに
    * 作成することで、
    *
    *     画像を右クリック → 送る → pypublish.js 
    *
    * の操作でエクスプローラから画像のはてなハイクへの
    * 投稿が可能になります。
    *
    */

   var PY = "c:\\Python26\\pythonw.exe";
   var args = WScript.Arguments;
   if(args.length != 1) return;
   var arg = args(0);
   var script = String(WScript.ScriptFullName).replace(/\.js$/,'.py');
   var cmdline = '"' + [
     PY ,
     script ,
     arg
   ].join('" "') + '"';
   WScript.Echo(cmdline);
   var wsh = new ActiveXObject('WScript.Shell');
   wsh.Exec(cmdline);

})();
