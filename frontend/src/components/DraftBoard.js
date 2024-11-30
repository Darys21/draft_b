import React from 'react';
import styled from 'styled-components';

const BoardContainer = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  height: calc(100vh - 80px);
  padding: 20px;
  background: #0f1624;
`;

const PicksList = styled.div`
  background: #1a2235;
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const MainContent = styled.div`
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 20px;
`;

const TeamsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  overflow-y: auto;
  padding: 10px;
`;

const PickItem = styled.div`
  background: ${props => props.isActive ? '#2d364d' : '#1f2937'};
  border-left: 4px solid ${props => props.isTop12 ? '#fbbf24' : '#60a5fa'};
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateX(5px);
  }
`;

const TeamCard = styled.div`
  background: #1a2235;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  
  h3 {
    color: #fff;
    margin-bottom: 15px;
    font-size: 1.2em;
    border-bottom: 2px solid #2d364d;
    padding-bottom: 10px;
  }
`;

const PlayersList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const PlayerCard = styled.div`
  background: #2d364d;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid ${props => props.isTop12 ? '#fbbf24' : '#60a5fa'};

  .player-name {
    color: #fff;
    font-weight: 600;
    margin-bottom: 5px;
  }

  .player-info {
    color: #9ca3af;
    font-size: 0.9em;
  }
`;

const DraftBoard = ({ picks, teams, currentPick }) => {
  return (
    <BoardContainer>
      <PicksList>
        <h2 style={{ color: '#fff', marginBottom: '20px' }}>Draft Picks</h2>
        {picks.map((pick, index) => (
          <PickItem 
            key={index}
            isActive={currentPick === index + 1}
            isTop12={pick.player.level === 1}
          >
            <div style={{ color: '#fff' }}>
              #{index + 1} {pick.team.name}
            </div>
            <div style={{ color: '#9ca3af' }}>
              {pick.player.name}
            </div>
          </PickItem>
        ))}
      </PicksList>

      <MainContent>
        <div style={{ color: '#fff', fontSize: '1.5em', padding: '0 10px' }}>
          Teams Draft Board
        </div>
        <TeamsGrid>
          {teams.map(team => (
            <TeamCard key={team.id}>
              <h3>{team.name}</h3>
              <PlayersList>
                {picks
                  .filter(pick => pick.team.id === team.id)
                  .map((pick, index) => (
                    <PlayerCard 
                      key={index}
                      isTop12={pick.player.level === 1}
                    >
                      <div className="player-name">{pick.player.name}</div>
                      <div className="player-info">
                        {pick.player.position} • Pick #{pick.pick_number}
                      </div>
                    </PlayerCard>
                  ))
                }
              </PlayersList>
            </TeamCard>
          ))}
        </TeamsGrid>
      </MainContent>
    </BoardContainer>
  );
};

export default DraftBoard;
