import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Button,
  Typography,
  Paper,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  IconButton,
  TablePagination,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Assignment as AssignmentIcon,
  BugReport as ProblemIcon,
  Lightbulb as SuggestionIcon,
} from '@mui/icons-material';
import { fetchSubmissions } from '../../store/submissionSlice';
import CreateSubmissionForm from '../components/molecules/CreateSubmissionForm';

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50];

const getTypeIcon = (type) => {
  switch (type) {
    case 'REPORT':
      return <AssignmentIcon />;
    case 'PROBLEM':
      return <ProblemIcon />;
    case 'SUGGESTION':
      return <SuggestionIcon />;
    default:
      return null;
  }
};

const getImportanceColor = (level) => {
  switch (level) {
    case 'HIGH':
      return 'error';
    case 'MEDIUM':
      return 'warning';
    case 'LOW':
      return 'info';
    default:
      return 'default';
  }
};

const SubmissionsPage = () => {
  const dispatch = useDispatch();
  const { items: submissions, total, loading, error } = useSelector((state) => state.submissions);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(ROWS_PER_PAGE_OPTIONS[0]);

  const loadSubmissions = () => {
    dispatch(fetchSubmissions({
      skip: page * rowsPerPage,
      limit: rowsPerPage,
    }));
  };

  useEffect(() => {
    loadSubmissions();
  }, [page, rowsPerPage]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Submissions
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadSubmissions}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            New Submission
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={2}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Importance</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Created At</TableCell>
                <TableCell>Task</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {submissions.map((submission) => (
                <TableRow key={submission.id}>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getTypeIcon(submission.type)}
                      {submission.type}
                    </Box>
                  </TableCell>
                  <TableCell>{submission.title}</TableCell>
                  <TableCell>{submission.description}</TableCell>
                  <TableCell>
                    <Chip 
                      label={submission.importance_level}
                      color={getImportanceColor(submission.importance_level)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{submission.creator?.full_name}</TableCell>
                  <TableCell>{formatDate(submission.created_at)}</TableCell>
                  <TableCell>
                    {submission.task_id ? (
                      <Typography variant="body2" color="primary">
                        Task #{submission.task_id}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No task
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {submissions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary">
                      No submissions found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      <CreateSubmissionForm
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </Box>
  );
};

export default SubmissionsPage;
