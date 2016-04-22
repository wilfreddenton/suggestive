(function(window) {
  var Ripples = function (initialState, setStateCallback) {
    this.state = initialState;
    this.events = {};
    this.eventTargets = {};
    this.setStateCallback = setStateCallback;
    for (var key in this.state) {
      var eventName = 'ripple' + key;
      this.events[eventName] = new Event(eventName);
      this.eventTargets[eventName] = [];
    }
  }
  Ripples.prototype.setState = function (newState) {
    for (var key in newState) {
      if (newState.hasOwnProperty(key)) {
        var eventName = 'ripple' + key;
        ripples.state[key] = newState[key];
        this.eventTargets[eventName].forEach(function (ele) {
          ele.dispatchEvent(this.events[eventName]);
        }.bind(this));
      }
    }
    if (typeof this.setStateCallback === 'function')
      this.setStateCallback();
  }
  Ripples.prototype.ripple = function (stateKeys, elements, reaction) {
    if (!Array.isArray(stateKeys))
      stateKeys = [stateKeys];
    if (!Array.isArray(elements))
      elements = [elements];
    stateKeys.forEach(function (key) {
      var eventName = 'ripple' + key;
      elements.forEach(function (element) {
        element.addEventListener(eventName, reaction);
        this.eventTargets[eventName].push(element);
      }.bind(this));
    }.bind(this));
  }
  Ripples.prototype.calm = function (stateKeys, elements, reaction) {
    if (!Array.isArray(stateKeys))
      stateKeys = [stateKeys];
    if (!Array.isArray(elements))
      elements = [elements];
    stateKeys.forEach(function (key) {
      var eventName = 'ripple' + key;
      elements.forEach(function (element) {
        element.removeEventListener(eventName, reaction);
        var i = this.eventTargets[eventName].indexOf(element);
        this.eventTargets[eventName].splice(i, 1);
      }.bind(this));
    }.bind(this));
  }
  Ripples.prototype.render = function (template) {
    if (typeof template[0] === 'string')
      template = [template];
    var docFrag = document.createDocumentFragment();
    template.forEach(function (subTemp) {
      var tag = subTemp[0], params = subTemp[1], children = subTemp[2];
      var element = document.createElement(tag);
      for (var key in params) {
        var param = params[key];
        if (typeof param === 'object' && param && !Array.isArray(param)) {
          for (var name in param)
            element[key][name] = param[name];
        } else { element[key] = param; }
      }
      if (Array.isArray(children)) {
        var childFrag = this.render(children);
        element.appendChild(childFrag);
      } else { element.innerHTML = children; }
      docFrag.appendChild(element);
    }.bind(this));
    return docFrag;
  }
  function debounce(func, wait, immediate) {
    var timeout;
    return function() {
      var context = this, args = arguments;
      var later = function() {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  };
  // initialization
  var state = {
    text: '',
    suggestions: [],
    messages: []
  };
  var ripples = new Ripples(state);
  var refs = {
    content: document.querySelector('.content'),
    textbox: document.getElementById('textbox'),
    suggestions: document.getElementById('suggestions'),
    history: document.querySelector('#history ul')
  };
  var rainbow = function(rel) {
    return 'hsl(' + (100 - (rel * 100)) + ',66%,80%)';
  }
  var suggestionTemplate = function(suggestion, i) {
    return (
      ['li', {className: 'suggestion', style: {background: rainbow(suggestion.relevance)}}, [
        ['div', {className: 'suggestion-number'}, i < 9 ? i + 1 : 0],
        ['span', {className: 'suggestion-text'}, suggestion.text]
      ]]
    );
  };
  var messageTemplate = function(message, i) {
    return (
      ['li', {className: 'message'}, [
        ['span', {className: 'message-text'}, message.text]
      ]]
    );
  }
  // handlers
  var baseUrl = 'http://localhost:5000/api';
  var postMessage = function() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && !xmlHttp.status == 200)
        console.log('error posting message');
    }
    xmlHttp.open("POST", baseUrl+"/message", true);
    xmlHttp.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    payload = {
      message: ripples.state.messages[ripples.state.messages.length - 1]
    }
    xmlHttp.send(JSON.stringify(payload));
  }
  var getSuggestions = function() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
        ripples.setState({ suggestions: JSON.parse(xmlHttp.responseText).suggestions.sort(function(a, b) {
          return b.text.toLowerCase() - a.text.toLowerCase();
        }) });
    }
    xmlHttp.open("GET", baseUrl+"/suggestions?text="+ripples.state.text, true);
    xmlHttp.send(null);
  }
  var test = debounce(function(e) {
    getSuggestions()
  }, 150);
  var enterHandler = function (e) {
    if (e.keyCode === 13 && e.metaKey) {
      var message = {text: refs.textbox.value.trim()}
      var messages = ripples.state.messages.slice();
      messages.push(message);
      ripples.setState({messages: messages});
      postMessage();
      if (refs.history.offsetHeight >= refs.content.offsetHeight*0.6) {
        var parent = refs.history.parentNode;
        if (!parent.classList.contains('static'))
          parent.classList.add('static');
        parent.scrollTop = parent.scrollHeight;
      }
      refs.textbox.value = '';
      ripples.setState({ text: refs.textbox.value })
      test();
    }
  }
  var inputHandler = function(e) {
    refs.textbox.style.height = '0px'
    refs.textbox.style.height = Math.max(50,this.scrollHeight)+'px';
    ripples.setState({ text: e.target.value });
    test(e);
  }
  var selectHandler = function(e) {
    var num = parseInt(this.childNodes[0].innerHTML)
    suggestion = ripples.state.suggestions[num == 0 ? 9 : num - 1].text;
    if (ripples.state.text.length > 0 && ripples.state.text.match(/\s+$/) === null) {
      suggestion = " " + suggestion;
    }
    refs.textbox.value += suggestion;
    ripples.setState({ text: refs.textbox.value });
    test();
  }
  var commandHandler = function(e) {
    if (e.keyCode >= 48 && e.keyCode <= 57) {
      if (e.metaKey) {
        var i = parseInt(String.fromCharCode(e.keyCode));
        if (i <= ripples.state.suggestions.length) {
          if (i === 0 && ripples.state.suggestions.length < 10)
            return false;
          refs.suggestions.childNodes[i == 0 ? 9 : i - 1].click();
        }
        event.preventDefault();
      }
    }
  }
  // reactions
  var suggestionsReaction = function() {
    var template = ripples.state.suggestions.map(suggestionTemplate);
    refs.suggestions.innerHTML = '';
    refs.suggestions.appendChild(ripples.render(template));
    Array.prototype.forEach.call(refs.suggestions.childNodes, function(suggestion) {
      suggestion.addEventListener('click', selectHandler, true);
    });
  }
  var historyReaction = function() {
    var template = ripples.state.messages.map(messageTemplate);
    refs.history.innerHTML = '';
    refs.history.appendChild(ripples.render(template));
  }
  // main
  ripples.ripple('suggestions', refs.suggestions, suggestionsReaction);
  ripples.ripple('messages', refs.history, historyReaction);
  refs.textbox.addEventListener('keyup', inputHandler);
  refs.textbox.addEventListener('keydown', enterHandler);
  window.addEventListener('keydown', commandHandler);
  getSuggestions();
})(window);
