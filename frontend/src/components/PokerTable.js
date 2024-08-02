import React, { useState, useEffect, useRef } from 'react';
import './PokerTable.css';

const PokerTable = () => {
  const [gameState, setGameState] = useState({
    pot: 0,
    currentPlayer: '-',
    currentBet: 0,
    oopPlayer: { name: 'OOP', chips: 0, hand: [] },
    ipPlayer: { name: 'IP', chips: 0, hand: [] },
    communityCards: [],
    street: '',
    lastAction: '',
  });
  const [messages, setMessages] = useState([]);
  const [validActions, setValidActions] = useState([]);
  const socketRef = useRef(null);
  const roomName = 'table1';
  const userId = 'player' + Math.floor(Math.random() * 1000);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    socketRef.current = new WebSocket(`ws://${window.location.host}/ws/poker/${roomName}/`);

    socketRef.current.onopen = () => {
      console.log('WebSocket connection established');
      addMessage('Connected to the poker table.');
    };

    socketRef.current.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log("Received message:", data);
      if (data.type === 'game_state') {
        console.log("Updating game state:", data);
        setGameState(data.game_state);
        socketRef.current.send(JSON.stringify({action: "ack_state", id: data.id}));
      } else if (data.type === 'sync') {
        socketRef.current.send(JSON.stringify({action: "ack_state", id: data.id}));
      } else if (data.type === 'private_hand') {
        updatePlayerHand(data.player, data.hand);
      } else if (data.type === 'request_action') {
        console.log("Handling action request:", data);
        setValidActions(data.valid_actions);
        addMessage("It's your turn. Please select an action.");
      } else if (data.error) {
        console.error("Received error:", data.error);
        addMessage(`Error: ${data.error}`);
      } else {
        console.log('Unknown message type:', data);
      }
    };

    socketRef.current.onclose = () => {
      console.error('Poker socket closed unexpectedly');
      addMessage('Disconnected from the poker table. Trying to reconnect...');
      setTimeout(connectWebSocket, 2000);
    };
  };

  const updatePlayerHand = (player, hand) => {
    setGameState(prevState => ({
      ...prevState,
      [player]: { ...prevState[player], hand }
    }));
  };

  const sendAction = (action) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        'type': 'player_action',
        'action': action,
        'user_id': userId,
        'room': roomName
      }));
      setValidActions([]);
    } else {
      console.error('WebSocket is not connected.');
    }
  };

  const addMessage = (message) => {
    setMessages(prevMessages => [...prevMessages, message]);
  };

  const startHand = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      console.log('Sending start_hand action');
      socketRef.current.send(JSON.stringify({
        'type': 'start_hand',
        'user_id': userId,
        'room': roomName
      }));
    } else {
      console.error('WebSocket is not connected.');
    }
  };

  return (
    <div id="poker-table">
      <h2>Poker Table</h2>
      <button onClick={startHand}>Start Hand</button>
      <PlayerHand player={gameState.oopPlayer} type="oop" />
      <CommunityCards cards={gameState.communityCards} street={gameState.street} />
      <div id="player-actions">
        {['check', 'call', 'bet', 'fold'].map(action => (
          <button 
            key={action} 
            onClick={() => sendAction(action)}
            disabled={!validActions.includes(action)}
          >
            {action.charAt(0).toUpperCase() + action.slice(1)}
          </button>
        ))}
      </div>
      <GameInfo 
        pot={gameState.pot} 
        currentPlayer={gameState.currentPlayer} 
        currentBet={gameState.currentBet} 
      />
      <PlayerHand player={gameState.ipPlayer} type="ip" />
      <MessageLog messages={messages} />
    </div>
  );
};

const PlayerHand = ({ player, type }) => (
  <div id={`${type}-player`} className="player-hand">
    <h3>{type.toUpperCase()} Player ({player.name})</h3>
    <p className="chips">Chips: {player.chips}</p>
    <div id={`${type}-cards`}>
      {player.hand.map((card, index) => (
        <span key={index} className="card">{card}</span>
      ))}
    </div>
  </div>
);

const CommunityCards = ({ cards, street }) => (
  <div id="community-cards" style={{ display: ['flop', 'turn', 'river'].includes(street) ? 'block' : 'none' }}>
    <h3>Community Cards</h3>
    {cards.map((card, index) => (
      <span key={index} className="card">{card}</span>
    ))}
  </div>
);

const GameInfo = ({ pot, currentPlayer, currentBet }) => (
  <div id="game-info">
    <p>Pot: ${pot}</p>
    <p>Current Player: {currentPlayer}</p>
    <p>Current Bet: ${currentBet}</p>
  </div>
);

const MessageLog = ({ messages }) => (
  <div id="message-log">
    {messages.map((message, index) => (
      <div key={index}>{message}</div>
    ))}
  </div>
);

export default PokerTable;