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
      for (var key in params)
        element[key] = params[key];
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
    suggestions: []
  };
  var ripples = new Ripples(state);
  var refs = {
    textbox: document.getElementById('textbox'),
    suggestions: document.getElementById('suggestions')
  };
  var suggestionTemplate = function(suggestion, i) {
    return (
      ['li', {className: 'suggestion'}, [
        ['div', {className: 'suggestion-number'}, i + 1],
        ['span', {className: 'suggestion-text'}, suggestion.text]
      ]]
    );
  };
  // handlers
  var baseUrl = 'http://localhost:5000/api';
  var getSuggestions = function() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
        ripples.setState({ suggestions: JSON.parse(xmlHttp.responseText).suggestions});
    }
    xmlHttp.open("GET", baseUrl+"/suggestions"+"?text="+ripples.state.text, true); // true for asynchronous
    xmlHttp.send(null);
  }
  var test = debounce(function(e) {
    getSuggestions()
  }, 100);
  var inputHandler = function(e) {
    ripples.setState({ text: e.target.value });
    test(e);
  }
  var selectHandler = function(e) {
    var num = parseInt(this.childNodes[0].innerHTML)
    console.log(num, ripples.state.suggestions.length)
    suggestion = ripples.state.suggestions[num - 1].text;
    if (ripples.state.text.match(/\s+$/) === null) {
      suggestion = " " + suggestion;
    }
    refs.textbox.value += suggestion;
    ripples.setState({ text: refs.textbox.value })
    test()
  }
  var commandHandler = function(e) {
    if (e.keyCode >= 48 && e.keyCode <= 57) {
      if (e.metaKey) {
        var i = parseInt(String.fromCharCode(e.keyCode));
        if (i <= ripples.state.suggestions.length) {
          refs.suggestions.childNodes[i - 1].click();
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
    })
  }
  // main
  ripples.ripple('suggestions', refs.suggestions, suggestionsReaction);
  refs.textbox.addEventListener('keyup', inputHandler);
  window.addEventListener('keydown', commandHandler);
  getSuggestions();
})(window);
