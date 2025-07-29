import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  IconButton,
  Menu,
  MenuItem,
  C          </Box>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          className="menu-button"
        >
          <MenuItem onClick={() => handleStatusChange('in_progress')}>
            Start Task
          </MenuItem>
          <MenuItem onClick={() => handleStatusChange('pending_review')}>
            Submit for Review
          </MenuItem>
          <MenuItem onClick={() => handleStatusChange('completed')}>
            Mark as Complete
          </MenuItem>
        </Menu>
      </CardContent>
      </CardActionArea>
    </Card>m '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { updateTaskStatus } from '../../store/taskSlice';

const priorityColors = {
  1: 'info',
  2: 'success',
  3: 'warning',
  4: 'error',
};

const priorityLabels = {
  1: 'Low',
  2: 'Medium',
  3: 'High',
  4: 'Urgent',
};

const statusColors = {
  new: 'info',
  in_progress: 'warning',
  pending_review: 'secondary',
  needs_revision: 'error',
  completed: 'success',
  canceled: 'default',
};

const TaskItem = ({ task, onSelect }) => {
  const dispatch = useDispatch();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (e) => {
    // Prevent the card click when clicking the menu
    if (e.target.closest('.menu-button')) {
      return;
    }
    onSelect(task);
  };

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleStatusChange = (newStatus) => {
    dispatch(updateTaskStatus({ taskId: task.id, status: newStatus }));
    handleMenuClose();
  };

  return (
    <Card sx={{ mb: 2, position: 'relative' }}>
      <CardActionArea onClick={handleClick}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box flex={1}>
              <Typography variant="h6" component="div" gutterBottom>
                {task.title}
              </Typography>
            
            {task.description && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2 }}
                noWrap
              >
                {task.description}
              </Typography>
            )}
            
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip
                label={priorityLabels[task.priority]}
                color={priorityColors[task.priority]}
                size="small"
              />
              <Chip
                label={task.status.replace('_', ' ')}
                color={statusColors[task.status]}
                size="small"
              />
              {task.assignee && (
                <Chip
                  icon={<PersonIcon />}
                  label={task.assignee.full_name}
                  size="small"
                  variant="outlined"
                />
              )}
              {task.due_date && (
                <Chip
                  icon={<ScheduleIcon />}
                  label={new Date(task.due_date).toLocaleDateString()}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>

          <IconButton
            size="small"
            onClick={handleMenuClick}
            sx={{ ml: 1 }}
            className="menu-button"
          >
            <MoreVertIcon />
          </IconButton>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => handleStatusChange('in_progress')}>
            Start Task
          </MenuItem>
          <MenuItem onClick={() => handleStatusChange('pending_review')}>
            Submit for Review
          </MenuItem>
          <MenuItem onClick={() => handleStatusChange('completed')}>
            Mark as Complete
          </MenuItem>
        </Menu>
      </CardContent>
    </Card>
  );
};

export default TaskItem;
